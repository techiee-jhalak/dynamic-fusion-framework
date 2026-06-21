import pandas as pd
import json
from pathlib import Path


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def save_all_formats(df: pd.DataFrame, out_dir: str, basename: str):
    ensure_dir(out_dir)
    csv_path = Path(out_dir) / f"{basename}.csv"
    parquet_path = Path(out_dir) / f"{basename}.parquet"
    json_path = Path(out_dir) / f"{basename}.json"
    df.to_csv(csv_path, index=False)
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        # parquet engine may be missing; skip if unavailable
        pass
    df.to_json(json_path, orient="records", lines=False)
    return dict(csv=str(csv_path), parquet=str(parquet_path), json=str(json_path))
