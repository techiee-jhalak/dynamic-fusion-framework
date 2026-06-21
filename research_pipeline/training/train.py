import argparse
import numpy as np
import pandas as pd
from research_pipeline.src.datasets.loader import load_csv
from research_pipeline.src.datasets.validator import detect_missing_values
from research_pipeline.src.stats.text_stats import text_statistics
from research_pipeline.src.noise.metrics import compute_noise_metrics
from research_pipeline.src.models.logistic_model import build_logistic_pipeline
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper
from research_pipeline.src.models.fusion_models import static_fusion, dynamic_noise_aware_fusion
from research_pipeline.training.utils import reproducibility_record
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
import json
import os
from pathlib import Path


def train_logistic(df, text_col, label_col, out_dir, seed=42):
    X = df[text_col].astype(str).tolist()
    y = df[label_col].astype(int).values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
    model = build_logistic_pipeline()
    model.fit(Xtr, ytr)
    preds = model.predict(Xte)
    acc = accuracy_score(yte, preds)
    pr, rc, f1, _ = precision_recall_fscore_support(yte, preds, average='binary')
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(out_dir, 'logistic_metrics.json'), 'w') as f:
        json.dump({'accuracy': acc, 'precision': pr, 'recall': rc, 'f1': f1}, f, indent=2)
    return model


def evaluate_baselines(df, text_col, label_col, out_dir, transformer_models=None):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    X = df[text_col].astype(str).tolist()
    y = df[label_col].astype(int).values
    results = {}
    # VADER
    vader = VaderWrapper()
    vader_probs = vader.predict_proba(X)
    vader_preds = vader_probs[:,1] >= 0.5
    acc = (vader_preds == y).mean()
    results['VADER'] = {'accuracy': float(acc)}
    # Transformers
    if transformer_models:
        for name, model_name in transformer_models.items():
            tw = TransformerWrapper(model_name)
            probs = tw.predict_proba(X)
            preds = probs.argmax(axis=1)
            acc = (preds == y).mean()
            results[name] = {'accuracy': float(acc)}
    # Save
    with open(os.path.join(out_dir, 'baseline_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    return results


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--out', default='research_pipeline/outputs')
    parser.add_argument('--text_col', default='text')
    parser.add_argument('--label_col', default='label')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    df = load_csv(args.input, text_col=args.text_col, label_col=args.label_col)
    missing = detect_missing_values(df)
    # enrich with text stats and noise
    stats = df[args.text_col].astype(str).map(text_statistics)
    stats_df = pd.DataFrame.from_records(list(stats))
    noise = stats_df.apply(lambda row: compute_noise_metrics(row.to_dict()), axis=1).tolist()
    noise_df = pd.DataFrame.from_records(noise)
    enriched = pd.concat([df.reset_index(drop=True), stats_df.reset_index(drop=True), noise_df], axis=1)
    # reproducibility
    reproducibility_record(args.out, [args.input], args.seed, {'model':'baseline-suite'})
    # train logistic as baseline
    train_logistic(enriched, args.text_col, args.label_col, args.out, seed=args.seed)
    # evaluate baselines
    evaluate_baselines(enriched, args.text_col, args.label_col, args.out, transformer_models={'DistilBERT':'distilbert-base-uncased-finetuned-sst-2-english','BERTweet':'vinai/bertweet-base'})


if __name__ == '__main__':
    cli()
