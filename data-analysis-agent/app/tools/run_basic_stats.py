from __future__ import annotations

import pandas as pd

TOOL_CONTRACT = {
    'name': 'run_basic_stats',
    'goal': 'Compute descriptive statistics and simple correlations for numeric columns.',
    'inputs': ['dataframe'],
    'outputs': ['stats_summary'],
    'must_not_do': ['fit predictive models or perform inferential testing'],
}


def run_basic_stats(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include='number')
    describe = numeric_df.describe().round(4).to_dict() if not numeric_df.empty else {}
    corr = numeric_df.corr(numeric_only=True).round(4).fillna(0).to_dict() if numeric_df.shape[1] > 1 else {}
    return {
        'numeric_columns': list(numeric_df.columns),
        'describe': describe,
        'correlations': corr,
    }
