from __future__ import annotations

from pydantic import BaseModel


class ReportResponse(BaseModel):
    analysis_id: str
    dataset_id: str
    status: str
    report_path: str | None
    artifact_paths: list[str]
    trace_id: str
    summary: dict
    trace_spans: list[dict]
