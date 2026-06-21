import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path


def save_hist(series: pd.Series, out_path: str, title: str = None, xlabel: str = None):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    sns.histplot(series.dropna(), kde=False)
    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_class_distribution(df: pd.DataFrame, label_col: str, out_path: str):
    vc = df[label_col].value_counts(dropna=False)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 4))
    sns.barplot(x=vc.index.astype(str), y=vc.values)
    plt.title('Class Distribution')
    plt.ylabel('count')
    plt.xlabel(label_col)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
