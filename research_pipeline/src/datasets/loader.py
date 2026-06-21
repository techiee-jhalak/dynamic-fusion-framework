import pandas as pd
from pathlib import Path
from typing import Optional


def load_csv(path: str, text_col: str = "text", label_col: Optional[str] = "label") -> pd.DataFrame:
    p = Path(path)
    if p.is_dir():
        files = list(p.glob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in {path}")
        df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    else:
        df = pd.read_csv(p)

    # ensure columns
    if text_col not in df.columns:
        raise KeyError(f"Text column '{text_col}' not found in {path}")
    if label_col and label_col not in df.columns:
        df[label_col] = None
    return df
