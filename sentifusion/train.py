from research_pipeline.training.engine import load_and_enrich, train_logistic_cv, evaluate_baselines, evaluate_fusion


def train(input_path, output_dir, text_col='text', label_col='label', seed=42, cv=5):
    enriched = load_and_enrich(input_path, text_col=text_col, label_col=label_col)
    baseline_res = evaluate_baselines(enriched, text_col, label_col, output_dir, transformer_models={
        'DistilBERT': 'distilbert-base-uncased-finetuned-sst-2-english',
        'BERTweet': 'vinai/bertweet-base'
    })
    fusion_res = evaluate_fusion(enriched, output_dir)
    log_res = train_logistic_cv(enriched, text_col, label_col, output_dir, seed=seed, cv=cv)
    return {'baseline': baseline_res, 'fusion': fusion_res, 'logistic_cv': log_res.to_dict(orient='records')}
