from __future__ import annotations

import uuid
from pathlib import Path

from app.agent.state import AgentState
from app.agent.tool_registry import ToolRegistry, tool_registry
from app.observability.logging import get_logger
from app.observability.tracing import TraceRecord, new_trace_id, traced_step
from app.schemas.analysis import AnalysisRequest
from app.services.cache_service import CacheService, cache
from app.services.dataframe_service import DataFrameService, dataframe_service
from app.services.report_service import ReportService, report_service

logger = get_logger(__name__)


class DataAnalysisOrchestrator:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
        cache_service: CacheService | None = None,
        dataframe_srv: DataFrameService | None = None,
        report_srv: ReportService | None = None,
    ) -> None:
        self.registry = registry or tool_registry
        self.cache = cache_service or cache
        self.dataframe_service = dataframe_srv or dataframe_service
        self.report_service = report_srv or report_service

    def create_analysis_state(self, dataset_id: str, trace_id: str | None = None) -> AgentState:
        analysis_id = f"an_{uuid.uuid4().hex[:10]}"
        state = AgentState(analysis_id=analysis_id, dataset_id=dataset_id, trace_id=trace_id or new_trace_id())
        self.cache.set_analysis(state.analysis_id, state.to_dict())
        return state

    def run_analysis(self, request: AnalysisRequest, analysis_id: str | None = None, trace_id: str | None = None) -> AgentState:
        dataset_meta = self.cache.get_dataset(request.dataset_id)
        if not dataset_meta:
            raise ValueError(f'Dataset not found: {request.dataset_id}')

        state = AgentState(
            analysis_id=analysis_id or f"an_{uuid.uuid4().hex[:10]}",
            dataset_id=request.dataset_id,
            trace_id=trace_id or new_trace_id(),
        )
        trace = TraceRecord(trace_id=state.trace_id)
        self.cache.set_analysis(state.analysis_id, state.to_dict())

        dataset_path = Path(dataset_meta['path'])
        output_dir = self.report_service.analysis_dir(state.analysis_id)

        try:
            with traced_step(trace, 'load_dataframe', dataset_id=request.dataset_id):
                state.begin_step('load_dataframe')
                df = self.dataframe_service.load_dataframe(dataset_path)

            with traced_step(trace, 'profile_dataset', rows=df.shape[0], cols=df.shape[1]):
                state.begin_step('profile_dataset')
                profile = self.registry.get('profile_dataset').fn(df)

            with traced_step(trace, 'summarize_columns', total_columns=df.shape[1]):
                state.begin_step('summarize_columns')
                column_summary = self.registry.get('summarize_columns').fn(df)

            with traced_step(trace, 'run_basic_stats', analysis_name=request.analysis_name):
                state.begin_step('run_basic_stats')
                stats = self.registry.get('run_basic_stats').fn(df)

            plot_paths: list[str] = []
            if request.include_plots:
                try:
                    with traced_step(trace, 'generate_plots', max_plots=request.max_plots):
                        state.begin_step('generate_plots')
                        plot_paths = self.registry.get('generate_plots').fn(df, str(output_dir), request.max_plots)
                        for path in plot_paths:
                            state.add_artifact(path)
                except Exception as exc:
                    state.mark_retry(f'generate_plots failed once: {exc}')
                    logger.warning('generate_plots.retry analysis_id=%s error=%s', state.analysis_id, exc)
                    with traced_step(trace, 'generate_plots_retry', max_plots=request.max_plots):
                        plot_paths = self.registry.get('generate_plots').fn(df, str(output_dir), request.max_plots)
                        for path in plot_paths:
                            state.add_artifact(path)
                    state.status = 'running'

            with traced_step(trace, 'write_report', artifact_count=len(plot_paths)):
                state.begin_step('write_report')
                report_path = self.registry.get('write_report').fn(
                    str(output_dir),
                    state.analysis_id,
                    request.dataset_id,
                    profile,
                    column_summary,
                    stats,
                    plot_paths,
                    state.warnings,
                )
                state.add_artifact(report_path)

            state.summary = {
                'profile': profile,
                'column_summary': column_summary,
                'stats': stats,
            }
            state.trace_spans = trace.spans
            state.mark_completed()
        except Exception as exc:
            logger.exception('analysis.failed analysis_id=%s', state.analysis_id)
            state.trace_spans = trace.spans
            state.mark_failed(str(exc))
        finally:
            self.cache.set_analysis(state.analysis_id, state.to_dict())

        return state


orchestrator = DataAnalysisOrchestrator()
