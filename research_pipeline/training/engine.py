import json
import os
import pickle
import re
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, wilcoxon
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from statsmodels.stats.contingency_tables import mcnemar

from research_pipeline.src.datasets.loader import load_csv
from research_pipeline.src.noise.metrics import compute_noise_metrics
from research_pipeline.src.stats.text_stats import text_statistics
from research_pipeline.src.models.fusion_models import dynamic_noise_aware_fusion, static_fusion
from research_pipeline.src.models.logistic_model import build_logistic_pipeline
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.training.utils import reproducibility_record
from research_pipeline.training.reporting import save_table


def normalize_labels(labels: pd.Series) -> Tuple[pd.Series, LabelEncoder]:
    if pd.api.types.is_integer_dtype(labels.dtype) or pd.api.types.is_float_dtype(labels.dtype):
        return labels.astype(int), None
    encoder = LabelEncoder()
    numeric = encoder.fit_transform(labels.astype(str))
    return pd.Series(numeric, index=labels.index), encoder


def load_and_enrich(path, text_col='text', label_col='label'):
    df = load_csv(path, text_col=text_col, label_col=label_col)
    stats = df[text_col].astype(str).map(text_statistics)
    stats_df = pd.DataFrame.from_records(list(stats))
    noise = stats_df.apply(lambda row: compute_noise_metrics(row.to_dict()), axis=1).tolist()
    noise_df = pd.DataFrame.from_records(noise)
    enriched = pd.concat([df.reset_index(drop=True), stats_df.reset_index(drop=True), noise_df], axis=1)
    if label_col in enriched.columns:
        enriched[label_col], _ = normalize_labels(enriched[label_col])
    return enriched


def compute_binary_metrics(y_true, y_pred):
    pr, rc, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    return {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(pr),
        'recall': float(rc),
        'f1': float(f1),
    }


def compute_roc_auc(y_true, proba):
    try:
        return float(roc_auc_score(y_true, proba[:, 1]))
    except Exception:
        return float('nan')


def measure_inference_time(model, texts, repeats=3):
    start = time.time()
    for _ in range(repeats):
        if callable(model):
            model(texts)
        else:
            model.predict(texts)
    return float((time.time() - start) / repeats)


def model_size_description(model):
    try:
        buffer = pickle.dumps(model)
        return f"{len(buffer)} bytes"
    except Exception:
        try:
            if hasattr(model, 'pipe') and hasattr(model.pipe, 'model'):
                params = sum(p.numel() for p in model.pipe.model.parameters())
                return f"{params / 1e6:.2f}M params"
            return 'unknown'
        except Exception:
            return 'unknown'


def baseline_predictions(enriched_df: pd.DataFrame, transformer_models: Dict[str, str]):
    X = enriched_df['text'].astype(str).tolist()
    preds = {}
    vader = VaderWrapper()
    preds['VADER'] = vader.predict(X)
    preds['VADER_proba'] = vader.predict_proba(X)
    for name, model_name in transformer_models.items():
        tw = TransformerWrapper(model_name)
        preds[name] = tw.predict(X)
        preds[f'{name}_proba'] = tw.predict_proba(X)
    return preds


def evaluate_baselines(enriched_df: pd.DataFrame, out_dir: str, transformer_models: Dict[str, str]) -> Dict[str, Dict]:
    y = enriched_df['label'].astype(int).to_numpy()
    X = enriched_df['text'].astype(str).tolist()
    vader = VaderWrapper()
    tw_models = {name: TransformerWrapper(model_name) for name, model_name in transformer_models.items()}
    preds = {'VADER': vader.predict(X), 'VADER_proba': vader.predict_proba(X)}
    for name, model in tw_models.items():
        preds[name] = model.predict(X)
        preds[f'{name}_proba'] = model.predict_proba(X)
    results = {}
    for name, model in tw_models.items():
        results[name] = {
            **compute_binary_metrics(y, preds[name]),
            'roc_auc': compute_roc_auc(y, preds[f'{name}_proba']),
            'inference_time': measure_inference_time(model, X),
            'model_size': model_size_description(model)
        }
    results['VADER'] = {
        **compute_binary_metrics(y, preds['VADER']),
        'roc_auc': compute_roc_auc(y, preds['VADER_proba']),
        'inference_time': measure_inference_time(vader, X),
        'model_size': model_size_description(vader)
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(out_dir) / 'baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    pd.DataFrame.from_dict(results, orient='index').reset_index().rename(columns={'index': 'Model'}).to_csv(Path(out_dir) / 'baseline_results.csv', index=False)
    return {'results': results, 'predictions': preds}


def evaluate_fusion(enriched_df: pd.DataFrame, out_dir: str, w1=0.1, w2=1.0) -> Dict[str, Dict]:
    X = enriched_df['text'].astype(str).tolist()
    y = enriched_df['label'].astype(int).to_numpy()
    vader = VaderWrapper()
    v_probs = vader.predict_proba(X)
    dist = TransformerWrapper('distilbert-base-uncased-finetuned-sst-2-english')
    d_probs = dist.predict_proba(X)
    static_preds, static_scores = static_fusion(v_probs, d_probs)
    dyn_preds, dyn_scores, alphas = dynamic_noise_aware_fusion(
        v_probs,
        d_probs,
        enriched_df['token_count'].fillna(1).astype(float).to_numpy(),
        enriched_df['N'].fillna(0).astype(float).to_numpy(),
        w1=w1,
        w2=w2,
    )

    def static_run(texts):
        return static_fusion(vader.predict_proba(texts), dist.predict_proba(texts))[0]

    def dynamic_run(texts):
        probs = dist.predict_proba(texts)
        return dynamic_noise_aware_fusion(VaderWrapper().predict_proba(texts), probs, enriched_df['token_count'].fillna(1).astype(float).to_numpy(), enriched_df['N'].fillna(0).astype(float).to_numpy(), w1=w1, w2=w2)[0]

    results = {
        'Static Fusion': {
            **compute_binary_metrics(y, static_preds),
            'roc_auc': compute_roc_auc(y, np.stack([1-static_scores, static_scores], axis=1)),
            'inference_time': measure_inference_time(static_run, X),
            'model_size': 'fusion-computed'
        },
        'Dynamic Fusion': {
            **compute_binary_metrics(y, dyn_preds),
            'roc_auc': compute_roc_auc(y, np.stack([1-dyn_scores, dyn_scores], axis=1)),
            'inference_time': measure_inference_time(dynamic_run, X),
            'model_size': 'fusion-computed'
        }
    }
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(out_dir) / 'fusion_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    pd.DataFrame.from_dict(results, orient='index').reset_index().rename(columns={'index': 'Model'}).to_csv(Path(out_dir) / 'fusion_results.csv', index=False)
    return {'results': results, 'predictions': {'Static Fusion': static_preds, 'Dynamic Fusion': dyn_preds}}


def train_logistic_cv(enriched_df: pd.DataFrame, text_col: str, label_col: str, out_dir: str, seed: int = 42, cv: int = 5):
    X = enriched_df[text_col].astype(str).tolist()
    y = enriched_df[label_col].astype(int).to_numpy()
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=seed)
    fold_results = []
    for train_idx, test_idx in skf.split(X, y):
        X_train = [X[i] for i in train_idx]
        X_test = [X[i] for i in test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]
        model = build_logistic_pipeline()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        fold_results.append(compute_binary_metrics(y_test, preds))
    results = pd.DataFrame(fold_results)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    results.to_csv(Path(out_dir) / f'logistic_cv_{cv}fold.csv', index=False)
    with open(Path(out_dir) / f'logistic_cv_{cv}fold.json', 'w') as f:
        json.dump(results.to_dict(orient='records'), f, indent=2)
    return results


def compute_significance(y_true, y_ref_pred, y_cmp_pred):
    tab = np.zeros((2, 2), dtype=int)
    for ref_right, cmp_right in zip(y_ref_pred == y_true, y_cmp_pred == y_true):
        tab[int(cmp_right), int(ref_right)] += 1
    try:
        mcnemar_result = mcnemar(tab, exact=False, correction=True)
        mcnemar_stats = {'mcnemar_stat': float(mcnemar_result.statistic), 'mcnemar_p': float(mcnemar_result.pvalue)}
    except Exception:
        mcnemar_stats = {'mcnemar_stat': np.nan, 'mcnemar_p': np.nan}
    t_stat, t_p = ttest_rel((y_ref_pred == y_true).astype(int), (y_cmp_pred == y_true).astype(int))
    try:
        w_stat, w_p = wilcoxon((y_ref_pred == y_true).astype(int), (y_cmp_pred == y_true).astype(int))
    except ValueError:
        w_stat, w_p = np.nan, np.nan
    return {
        **mcnemar_stats,
        'paired_t_stat': float(t_stat),
        'paired_t_p': float(t_p),
        'wilcoxon_stat': float(w_stat),
        'wilcoxon_p': float(w_p),
    }


def statistical_significance(enriched_df: pd.DataFrame, out_dir: str):
    baselines = evaluate_baselines(enriched_df, out_dir, transformer_models={
        'DistilBERT': 'distilbert-base-uncased-finetuned-sst-2-english',
        'BERTweet': 'vinai/bertweet-base',
    })
    fusion = evaluate_fusion(enriched_df, out_dir)
    y = enriched_df['label'].astype(int).to_numpy()
    dynamic_preds = fusion['predictions']['Dynamic Fusion']
    comparisons = {
        'VADER': baselines['predictions']['VADER'],
        'DistilBERT': baselines['predictions']['DistilBERT'],
        'BERTweet': baselines['predictions']['BERTweet'],
        'Static Fusion': fusion['predictions']['Static Fusion'],
    }
    records = []
    for name, preds in comparisons.items():
        stats = compute_significance(y, dynamic_preds, preds)
        records.append({'Comparison': f'Dynamic vs {name}', **stats})
    df = pd.DataFrame(records)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(Path(out_dir) / 'statistical_significance.csv', index=False)
    return df


def ablation_metrics(enriched_df: pd.DataFrame, out_dir: str, w1=0.1, w2=1.0):
    X = enriched_df['text'].astype(str).tolist()
    y = enriched_df['label'].astype(int).to_numpy()
    vader = VaderWrapper()
    v_probs = vader.predict_proba(X)
    dist = TransformerWrapper('distilbert-base-uncased-finetuned-sst-2-english')
    d_probs = dist.predict_proba(X)
    lengths = enriched_df['token_count'].fillna(1).astype(float).to_numpy()
    noise = enriched_df['N'].fillna(0).astype(float).to_numpy()
    results = {}
    preds, _ = static_fusion(v_probs, d_probs)
    results['Static Fusion'] = compute_binary_metrics(y, preds)
    length_preds, _, _ = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=w1, w2=0.0)
    results['Length-Aware'] = compute_binary_metrics(y, length_preds)
    noise_preds, _, _ = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=0.0, w2=w2)
    results['Noise-Aware'] = compute_binary_metrics(y, noise_preds)
    full_preds, _, _ = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=w1, w2=w2)
    results['Full Dynamic'] = compute_binary_metrics(y, full_preds)
    df = pd.DataFrame([{'Variant': k, **v} for k, v in results.items()])
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(Path(out_dir) / 'ablation_study.csv', index=False)
    return df


def noise_bins(enriched_df: pd.DataFrame):
    bins = pd.cut(enriched_df['N'], bins=[-1, 0.33, 0.66, 1.0], labels=['Low Noise', 'Medium Noise', 'High Noise'])
    return bins


def noise_sensitivity_data(enriched_df: pd.DataFrame):
    results = evaluate_baselines(enriched_df, 'research_pipeline/outputs', transformer_models={
        'DistilBERT': 'distilbert-base-uncased-finetuned-sst-2-english',
        'BERTweet': 'vinai/bertweet-base',
    })
    fusion = evaluate_fusion(enriched_df, 'research_pipeline/outputs')
    y = enriched_df['label'].astype(int).to_numpy()
    preds = {
        'VADER': results['predictions']['VADER'],
        'DistilBERT': results['predictions']['DistilBERT'],
        'BERTweet': results['predictions']['BERTweet'],
        'Static Fusion': fusion['predictions']['Static Fusion'],
        'Dynamic Fusion': fusion['predictions']['Dynamic Fusion'],
    }
    noise_cat = noise_bins(enriched_df)
    rows = []
    for label in noise_cat.cat.categories:
        idx = noise_cat == label
        if idx.sum() == 0:
            continue
        y_sub = y[idx]
        for model_name, pred_array in preds.items():
            rows.append({
                'noise_bin': label,
                'Model': model_name,
                'accuracy': float((pred_array[idx] == y_sub).mean()),
            })
    return pd.DataFrame(rows)


def error_analysis(enriched_df: pd.DataFrame, out_dir: str):
    def categorize(text):
        text = str(text).lower()
        categories = []
        if any(s in text for s in ['lol', 'jk', 'yeah right', 'as if', 'sarcasm']):
            categories.append('Sarcasm')
        if any(ch in text for ch in ['😊', '😂', '😒', '😢', '❤️']):
            categories.append('Emoji Ambiguity')
        if ' ' in text and any(ord(ch) > 127 for ch in text):
            categories.append('Code-Mixing')
        if re.search(r'[a-z]+[0-9]+|[0-9]+[a-z]+', text):
            categories.append('Transliteration')
        if len(text.split()) > 25:
            categories.append('Context')
        return categories or ['Other']

    categories = []
    for _, row in enriched_df.iterrows():
        categories.extend(categorize(row['text']))
    counts = pd.Series(categories).value_counts().rename_axis('category').reset_index(name='count')
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    counts.to_csv(Path(out_dir) / 'error_analysis.csv', index=False)
    with open(Path(out_dir) / 'error_analysis.json', 'w') as f:
        json.dump(counts.to_dict(orient='records'), f, indent=2)
    return counts


def noise_component_contribution(enriched_df: pd.DataFrame, out_dir: str):
    comp = enriched_df[['E', 'R', 'C', 'S']].mean().reset_index()
    comp.columns = ['component', 'value']
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    comp.to_csv(Path(out_dir) / 'noise_component_contribution.csv', index=False)
    return comp


def generate_document_outputs(tables: Dict[str, pd.DataFrame], figures: Dict[str, Path], out_dir: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        base = Path(out_dir) / name
        df.to_csv(str(base) + '.csv', index=False)
        try:
            df.to_excel(str(base) + '.xlsx', index=False)
        except Exception:
            pass
        try:
            with open(str(base) + '.tex', 'w') as f:
                f.write(df.to_latex(index=False))
        except Exception:
            pass
    for _, fig_path in figures.items():
        target = Path(out_dir) / fig_path.name
        if fig_path.exists():
            target.write_bytes(fig_path.read_bytes())
    return True
