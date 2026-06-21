import pandas as pd
from .text_stats import text_statistics


def dataset_statistics(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    stats = {}
    stats['n_samples'] = len(df)
    texts = df[text_col].astype(str)
    stats['avg_char_len'] = texts.map(len).mean()
    stats['median_char_len'] = texts.map(len).median()
    stats['avg_token_len'] = texts.map(lambda t: len(t.split())).mean()
    stats['median_token_len'] = texts.map(lambda t: len(t.split())).median()
    return pd.DataFrame.from_dict(stats, orient='index', columns=['value'])
