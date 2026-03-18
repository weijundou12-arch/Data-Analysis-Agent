from __future__ import annotations

import pandas as pd

TOOL_CONTRACT = {
    'name': 'profile_dataset',
    'goal': 'Compute high-level dataset metadata and missingness summary.',
    'inputs': ['dataframe'],
    'outputs': ['profile_summary'],
    'must_not_do': ['mutate the source dataframe'],
}


def profile_dataset(df: pd.DataFrame) -> dict:
    missing = df.isna().sum().to_dict()
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    return {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'column_names': list(df.columns),
        'dtypes': dtypes,
        'missing_values': {k: int(v) for k, v in missing.items()},
        'duplicate_rows': int(df.duplicated().sum()),
    }
