import os
from pathlib import Path

import pandas as pd

from app.agent.orchestrator import DataAnalysisOrchestrator
from app.schemas.analysis import AnalysisRequest
from app.services.cache_service import CacheService
from app.services.dataframe_service import DataFrameService
from app.services.report_service import ReportService


def test_orchestrator_runs_complete_workflow(tmp_path):
    csv_path = tmp_path / 'sample.csv'
    pd.DataFrame({'age': [21, 30, 33], 'score': [88, 92, 95], 'group': ['a', 'a', 'b']}).to_csv(csv_path, index=False)

    cache = CacheService()
    dataframe_service = DataFrameService(base_dir=str(tmp_path))
    report_service = ReportService(base_dir=str(tmp_path))
    orchestrator = DataAnalysisOrchestrator(cache_service=cache, dataframe_srv=dataframe_service, report_srv=report_service)

    cache.set_dataset('ds_local', {'dataset_id': 'ds_local', 'path': str(csv_path), 'filename': 'sample.csv'})
    state = orchestrator.run_analysis(AnalysisRequest(dataset_id='ds_local', include_plots=True, max_plots=2))

    assert state.status == 'completed'
    assert any(path.endswith('report.md') for path in state.artifact_paths)
    report_path = next(path for path in state.artifact_paths if path.endswith('report.md'))
    assert Path(report_path).exists()
