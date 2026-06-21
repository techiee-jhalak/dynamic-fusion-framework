from research_pipeline.training.engine import load_and_enrich, evaluate_baselines, evaluate_fusion, ablation_metrics, error_analysis, compute_significance
import pandas as pd
from pathlib import Path


def generate_paper_results(input_path, output_dir, text_col='text', label_col='label'):
    enriched = load_and_enrich(input_path, text_col=text_col, label_col=label_col)
    baselines = evaluate_baselines(enriched, text_col, label_col, output_dir, transformer_models={
        'DistilBERT': 'distilbert-base-uncased-finetuned-sst-2-english',
        'BERTweet': 'vinai/bertweet-base'
    })
    fusion = evaluate_fusion(enriched, output_dir)
    ablation = ablation_metrics(enriched)
    error = error_analysis(enriched, output_dir)
    # build report tables
    table7 = pd.DataFrame([{'Model': m, **metrics} for m, metrics in {**baselines, **fusion}.items()])
    table8 = []
    dynamic_preds = None
    if 'Dynamic Fusion' in fusion:
        dynamic_preds = 'Dynamic Fusion'
    # placeholder - real predictions required
    table8 = pd.DataFrame([{'Comparison': 'Dynamic vs VADER', 'mcnemar_p': None, 'paired_t_p': None, 'wilcoxon_p': None}])
    table9 = pd.DataFrame([{'Variant': k, **v} for k, v in ablation.items()])
    table10 = error
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    table7.to_csv(Path(output_dir) / 'table7_overall_performance.csv', index=False)
    table8.to_csv(Path(output_dir) / 'table8_statistical_significance.csv', index=False)
    table9.to_csv(Path(output_dir) / 'table9_ablation_study.csv', index=False)
    table10.to_csv(Path(output_dir) / 'table10_error_analysis.csv', index=False)
    return {'table7': table7, 'table8': table8, 'table9': table9, 'table10': table10}
