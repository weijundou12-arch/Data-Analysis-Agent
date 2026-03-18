import pandas as pd

from app.tools.profile_dataset import profile_dataset
from app.tools.run_basic_stats import run_basic_stats
from app.tools.summarize_columns import summarize_columns


def test_profile_dataset_counts_missing_and_duplicates():
    df = pd.DataFrame({'a': [1, 2, None, 2], 'b': ['x', 'y', 'y', 'y']})
    result = profile_dataset(df)
    assert result['rows'] == 4
    assert result['columns'] == 2
    assert result['missing_values']['a'] == 1


def test_column_summaries_capture_numeric_and_categorical():
    df = pd.DataFrame({'age': [10, 20, 30], 'group': ['a', 'a', 'b']})
    result = summarize_columns(df)
    assert result['age']['type'] == 'numeric'
    assert result['group']['type'] == 'categorical'


def test_basic_stats_returns_describe_and_correlations():
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})
    result = run_basic_stats(df)
    assert 'x' in result['describe']
    assert result['correlations']['x']['y'] == 1.0
