from __future__ import annotations

import pandas as pd

TOOL_CONTRACT = {
    'name': 'summarize_columns',
    'goal': 'Generate per-column summaries for numeric and categorical features.',
    'inputs': ['dataframe'],
    'outputs': ['column_summaries'],
    'must_not_do': ['drop columns or impute missing values'],
}


def summarize_columns(df: pd.DataFrame, top_k: int = 3) -> dict:
    summary: dict[str, dict] = {}
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            summary[col] = {
                'type': 'numeric',
                'mean': None if series.dropna().empty else round(float(series.mean()), 4),
                'std': None if series.dropna().empty else round(float(series.std()), 4),
                'min': None if series.dropna().empty else round(float(series.min()), 4),
                'max': None if series.dropna().empty else round(float(series.max()), 4),
            }
        else:
            value_counts = series.fillna('<NA>').astype(str).value_counts().head(top_k)
            summary[col] = {
                'type': 'categorical',
                'unique': int(series.nunique(dropna=True)),
                'top_values': value_counts.to_dict(),
            }
    return summary
