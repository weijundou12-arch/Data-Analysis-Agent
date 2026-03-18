from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.agent.orchestrator import orchestrator
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.cache_service import cache

router = APIRouter(prefix='/analyze', tags=['analyze'])


def _run_in_background(request: AnalysisRequest, analysis_id: str, trace_id: str) -> None:
    orchestrator.run_analysis(request=request, analysis_id=analysis_id, trace_id=trace_id)


@router.post('', response_model=AnalysisResponse)
def analyze_dataset(request: AnalysisRequest, background_tasks: BackgroundTasks) -> AnalysisResponse:
    if not cache.get_dataset(request.dataset_id):
        raise HTTPException(status_code=404, detail='Dataset not found')

    seed_state = orchestrator.create_analysis_state(request.dataset_id)
    if request.run_in_background:
        background_tasks.add_task(_run_in_background, request, seed_state.analysis_id, seed_state.trace_id)
        return AnalysisResponse(
            analysis_id=seed_state.analysis_id,
            dataset_id=request.dataset_id,
            status='pending',
            current_step='queued',
            report_path=None,
            trace_id=seed_state.trace_id,
            artifact_paths=[],
            warnings=[],
        )

    final_state = orchestrator.run_analysis(request=request, analysis_id=seed_state.analysis_id, trace_id=seed_state.trace_id)
    return AnalysisResponse(
        analysis_id=final_state.analysis_id,
        dataset_id=final_state.dataset_id,
        status=final_state.status,
        current_step=final_state.current_step,
        report_path=next((p for p in final_state.artifact_paths if p.endswith('report.md')), None),
        trace_id=final_state.trace_id,
        artifact_paths=final_state.artifact_paths,
        warnings=final_state.warnings + final_state.errors,
    )


@router.get('/{analysis_id}', response_model=AnalysisResponse)
def get_analysis_status(analysis_id: str) -> AnalysisResponse:
    payload = cache.get_analysis(analysis_id)
    if not payload:
        raise HTTPException(status_code=404, detail='Analysis not found')
    return AnalysisResponse(
        analysis_id=payload['analysis_id'],
        dataset_id=payload['dataset_id'],
        status=payload['status'],
        current_step=payload.get('current_step'),
        report_path=next((p for p in payload.get('artifact_paths', []) if p.endswith('report.md')), None),
        trace_id=payload['trace_id'],
        artifact_paths=payload.get('artifact_paths', []),
        warnings=payload.get('warnings', []) + payload.get('errors', []),
    )
