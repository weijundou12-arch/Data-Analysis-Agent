from __future__ import annotations

import os
from pathlib import Path

from app.observability.logging import get_logger

logger = get_logger(__name__)


class ReportService:
    def __init__(self, base_dir: str | None = None) -> None:
        home = base_dir or os.getenv('DATA_ANALYSIS_AGENT_HOME', './runtime')
        self.base_dir = Path(home)
        self.report_dir = self.base_dir / 'reports'
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def analysis_dir(self, analysis_id: str) -> Path:
        path = self.report_dir / analysis_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_text_report(self, analysis_id: str, content: str) -> str:
        path = self.analysis_dir(analysis_id) / 'report.md'
        path.write_text(content, encoding='utf-8')
        logger.info('report.written analysis_id=%s path=%s', analysis_id, path)
        return str(path)


report_service = ReportService()
