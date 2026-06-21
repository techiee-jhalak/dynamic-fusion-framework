import argparse
import pandas as pd
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper
from research_pipeline.src.models.fusion_models import dynamic_noise_aware_fusion


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--out', default='research_pipeline/outputs/predictions.csv')
    parser.add_argument('--w1', type=float, default=0.1)
    parser.add_argument('--w2', type=float, default=1.0)
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    X = df['text'].astype(str).tolist()
    vader = VaderWrapper()
    v_probs = vader.predict_proba(X)
    dist = TransformerWrapper('distilbert-base-uncased-finetuned-sst-2-english')
    d_probs = dist.predict_proba(X)
    lengths = df['token_count'].fillna(1).astype(float).values
    noise = df['N'].fillna(0).astype(float).values
    preds, scores, alphas = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=args.w1, w2=args.w2)
    out_df = df.copy()
    out_df['pred'] = preds
    out_df['score'] = scores
    out_df['alpha'] = alphas
    out_df.to_csv(args.out, index=False)
    print('Predictions saved to', args.out)


if __name__ == '__main__':
    cli()
