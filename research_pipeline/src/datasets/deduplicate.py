import pandas as pd


def find_exact_duplicates(df: pd.DataFrame, col: str = "text") -> pd.DataFrame:
    if col not in df.columns:
        return pd.DataFrame()
    dup = df[df.duplicated(subset=[col], keep=False)].copy()
    return dup


def unique_by_hash(df: pd.DataFrame, col: str = "text") -> pd.DataFrame:
    # simple stable dedupe keeping first
    if col not in df.columns:
        return df
    return df.drop_duplicates(subset=[col], keep="first").reset_index(drop=True)
