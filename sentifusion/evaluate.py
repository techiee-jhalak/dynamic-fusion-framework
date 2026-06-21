import pandas as pd
from research_pipeline.training.engine import load_and_enrich, evaluate_fusion


def evaluate(input_path, output_dir, text_col='text', label_col='label'):
    enriched = load_and_enrich(input_path, text_col=text_col, label_col=label_col)
    return evaluate_fusion(enriched, output_dir)
