from __future__ import annotations

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    dataset_id: str
    analysis_name: str = Field(default='default-analysis')
    include_plots: bool = True
    max_plots: int = Field(default=3, ge=1, le=10)
    run_in_background: bool = False


class AnalysisResponse(BaseModel):
    analysis_id: str
    dataset_id: str
    status: str
    current_step: str | None = None
    report_path: str | None = None
    trace_id: str
    artifact_paths: list[str] = []
    warnings: list[str] = []
