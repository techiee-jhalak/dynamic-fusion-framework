import pandas as pd
from research_pipeline.src.models.vader_model import VaderWrapper
from research_pipeline.src.models.transformer_wrapper import TransformerWrapper
from research_pipeline.src.models.fusion_models import dynamic_noise_aware_fusion


def predict(input_path, output_path, w1=0.1, w2=1.0):
    df = pd.read_csv(input_path)
    X = df['text'].astype(str).tolist()
    vader = VaderWrapper()
    v_probs = vader.predict_proba(X)
    dist = TransformerWrapper('distilbert-base-uncased-finetuned-sst-2-english')
    d_probs = dist.predict_proba(X)
    lengths = df['token_count'].fillna(1).astype(float).values
    noise = df['N'].fillna(0).astype(float).values
    preds, scores, alphas = dynamic_noise_aware_fusion(v_probs, d_probs, lengths, noise, w1=w1, w2=w2)
    df['pred'] = preds
    df['score'] = scores
    df['alpha'] = alphas
    df.to_csv(output_path, index=False)
    return df
