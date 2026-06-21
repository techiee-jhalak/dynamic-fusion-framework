import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os


def save_table(df: pd.DataFrame, path_base: str):
    Path(os.path.dirname(path_base)).mkdir(parents=True, exist_ok=True)
    df.to_csv(path_base + '.csv', index=False)
    try:
        df.to_excel(path_base + '.xlsx', index=False)
    except Exception:
        pass
    try:
        with open(path_base + '.tex', 'w') as f:
            f.write(df.to_latex(index=False))
    except Exception:
        pass


def bar_metrics(df_metrics: pd.DataFrame, out_png: str):
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    df = df_metrics.set_index('Model')
    df.plot.bar(rot=0)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


def noise_sensitivity_plot(df: pd.DataFrame, out_png: str):
    # df expected columns: ['noise_bin','Model','accuracy']
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    sns.lineplot(data=df, x='noise_bin', y='accuracy', hue='Model', marker='o')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.savefig(out_png.replace('.png', '.svg'))
    plt.savefig(out_png.replace('.png', '.pdf'))
    plt.close()


def ablation_plot(df: pd.DataFrame, out_png: str):
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    df2 = df.set_index('Variant')
    df2.plot.bar(rot=0)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.savefig(out_png.replace('.png', '.svg'))
    plt.savefig(out_png.replace('.png', '.pdf'))
    plt.close()


def error_distribution_plot(df: pd.DataFrame, out_png: str):
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    sns.barplot(data=df, x='category', y='count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.savefig(out_png.replace('.png', '.svg'))
    plt.savefig(out_png.replace('.png', '.pdf'))
    plt.close()
