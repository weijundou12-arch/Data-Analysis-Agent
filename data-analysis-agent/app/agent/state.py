from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class AgentState:
    analysis_id: str
    dataset_id: str
    trace_id: str
    status: str = 'pending'
    current_step: str | None = None
    retries: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    trace_spans: list[dict] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None

    def begin_step(self, step: str) -> None:
        self.status = 'running'
        self.current_step = step

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_artifact(self, path: str) -> None:
        self.artifact_paths.append(path)

    def mark_retry(self, reason: str) -> None:
        self.retries += 1
        self.status = 'retrying'
        self.errors.append(reason)

    def mark_failed(self, reason: str) -> None:
        self.status = 'failed'
        self.errors.append(reason)
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def mark_completed(self) -> None:
        self.status = 'completed'
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)
