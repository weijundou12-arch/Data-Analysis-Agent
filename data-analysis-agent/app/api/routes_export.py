from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.report import ReportResponse
from app.services.cache_service import cache

router = APIRouter(prefix='/export', tags=['export'])


@router.get('/{analysis_id}', response_model=ReportResponse)
def export_report(analysis_id: str) -> ReportResponse:
    payload = cache.get_analysis(analysis_id)
    if not payload:
        raise HTTPException(status_code=404, detail='Analysis not found')
    report_path = next((p for p in payload.get('artifact_paths', []) if p.endswith('report.md')), None)
    return ReportResponse(
        analysis_id=payload['analysis_id'],
        dataset_id=payload['dataset_id'],
        status=payload['status'],
        report_path=report_path,
        artifact_paths=payload.get('artifact_paths', []),
        trace_id=payload['trace_id'],
        summary=payload.get('summary', {}),
        trace_spans=payload.get('trace_spans', []),
    )
