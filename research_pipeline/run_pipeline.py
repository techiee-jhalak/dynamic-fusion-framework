"""CLI runner to execute the full research pipeline:
- load dataset(s)
- validate
- compute per-sample stats and noise metrics
- save outputs (CSV, Parquet, JSON)
- generate figures
"""
import argparse
from research_pipeline.src.datasets.loader import load_csv
from research_pipeline.src.datasets.validator import (
    detect_missing_values,
    class_distribution,
)
from research_pipeline.src.datasets.deduplicate import find_exact_duplicates
from research_pipeline.src.stats.text_stats import text_statistics
from research_pipeline.src.noise.metrics import compute_noise_metrics
from research_pipeline.src.utils.io import save_all_formats, ensure_dir
from research_pipeline.src.visualization.plots import save_hist, plot_class_distribution
import pandas as pd
from pathlib import Path


def enrich_df(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    stats = df[text_col].astype(str).map(text_statistics)
    stats_df = pd.DataFrame.from_records(list(stats))
    noise = stats_df.apply(lambda row: compute_noise_metrics(row.to_dict()), axis=1).tolist()
    noise_df = pd.DataFrame.from_records(noise)
    out = pd.concat([df.reset_index(drop=True), stats_df.reset_index(drop=True), noise_df], axis=1)
    return out


def run(path: str, out_dir: str, text_col: str = "text", label_col: str = "label"):
    df = load_csv(path, text_col=text_col, label_col=label_col)
    ensure_dir(out_dir)

    # validation
    missing = detect_missing_values(df)
    duplicates = find_exact_duplicates(df, col=text_col)

    # enrich with stats and noise
    enriched = enrich_df(df, text_col=text_col)

    # save full enriched dataset
    save_all_formats(enriched, out_dir, "enriched_dataset")
    save_all_formats(missing.reset_index(), out_dir, "missing_values")
    save_all_formats(duplicates.reset_index(), out_dir, "duplicates")

    # dataset and noise stats
    dataset_stats = {
        'n_samples': len(df),
        'n_duplicates': len(duplicates),
        'n_missing_values': int(missing.sum().sum()),
    }
    pd.DataFrame.from_dict(dataset_stats, orient='index', columns=['value']).to_csv(Path(out_dir)/"dataset_statistics.csv")

    noise_table = enriched[['E','R','C','S','N']].describe()
    noise_table.to_csv(Path(out_dir)/"noise_statistics.csv")

    # visualizations
    save_hist(enriched['N'], str(Path(out_dir)/"noise_distribution.png"), title='Noise Distribution', xlabel='N')
    save_hist(enriched['E'], str(Path(out_dir)/"emoji_density_distribution.png"), title='Emoji Density', xlabel='E')
    save_hist(enriched['C'], str(Path(out_dir)/"code_mixing_distribution.png"), title='Code-Mixing Ratio', xlabel='C')
    save_hist(enriched['S'], str(Path(out_dir)/"symbol_density_distribution.png"), title='Symbol Density', xlabel='S')
    if label_col in enriched.columns:
        plot_class_distribution(enriched, label_col, str(Path(out_dir)/"class_distribution.png"))

    print("Pipeline complete. Outputs in:", out_dir)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to CSV or directory with CSVs')
    parser.add_argument('--out', default='research_pipeline/outputs', help='Output directory')
    parser.add_argument('--text_col', default='text')
    parser.add_argument('--label_col', default='label')
    args = parser.parse_args()
    run(args.input, args.out, args.text_col, args.label_col)


if __name__ == '__main__':
    cli()
