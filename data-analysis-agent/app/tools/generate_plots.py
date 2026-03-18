from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

TOOL_CONTRACT = {
    'name': 'generate_plots',
    'goal': 'Generate basic univariate histograms for numeric columns.',
    'inputs': ['dataframe', 'output_dir'],
    'outputs': ['plot_paths'],
    'must_not_do': ['open GUI windows or modify the dataframe'],
}


def generate_plots(df: pd.DataFrame, output_dir: str, max_plots: int = 3) -> list[str]:
    numeric_cols = list(df.select_dtypes(include='number').columns)[:max_plots]
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    plot_paths: list[str] = []
    for col in numeric_cols:
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].dropna().plot.hist(ax=ax, bins=20)
        ax.set_title(f'Distribution of {col}')
        ax.set_xlabel(col)
        path = out / f'{col}_hist.png'
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        plot_paths.append(str(path))
    return plot_paths
