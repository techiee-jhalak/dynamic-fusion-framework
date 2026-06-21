import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from research_pipeline.src.models.fusion_models import static_fusion, dynamic_noise_aware_fusion
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper


def compute_metrics(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    pr, rc, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    return {'accuracy': float(acc), 'precision': float(pr), 'recall': float(rc), 'f1': float(f1)}


def evaluate_fusion(enriched_df, out_dir, w1=0.1, w2=1.0):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    X = enriched_df['text'].astype(str).tolist()
    y = enriched_df['label'].astype(int).values
    vader = VaderWrapper()
    v_probs = vader.predict_proba(X)
    dist = TransformerWrapper('distilbert-base-uncased-finetuned-sst-2-english')
    d_probs = dist.predict_proba(X)
    # static
    static_preds, static_scores = static_fusion(v_probs, d_probs)
    static_metrics = compute_metrics(y, static_preds)
    # dynamic
    lengths = enriched_df['token_count'].fillna(1).astype(float).values
    noise = enriched_df['N'].fillna(0).astype(float).values
    dyn_preds, dyn_scores, alphas = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=w1, w2=w2)
    dyn_metrics = compute_metrics(y, dyn_preds)
    out = {'static': static_metrics, 'dynamic': dyn_metrics}
    with open(Path(out_dir)/'fusion_evaluation.json','w') as f:
        json.dump(out, f, indent=2)
    return out


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--enriched', required=True)
    parser.add_argument('--out', default='research_pipeline/outputs')
    args = parser.parse_args()
    df = pd.read_csv(args.enriched)
    evaluate_fusion(df, args.out)

if __name__ == '__main__':
    cli()
