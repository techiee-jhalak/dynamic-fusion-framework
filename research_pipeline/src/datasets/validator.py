import pandas as pd
from typing import List


def required_columns(df: pd.DataFrame, cols: List[str]) -> List[str]:
    missing = [c for c in cols if c not in df.columns]
    return missing


def detect_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    # returns missing value counts per column
    return df.isna().sum().to_frame(name="missing_count")


def detect_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
    if subset is None:
        subset = [c for c in df.columns]
    dup_mask = df.duplicated(subset=subset, keep=False)
    return df[dup_mask]


def class_distribution(df: pd.DataFrame, label_col: str = "label") -> pd.DataFrame:
    if label_col not in df.columns:
        return pd.DataFrame()
    return df[label_col].value_counts(dropna=False).to_frame(name="count")
