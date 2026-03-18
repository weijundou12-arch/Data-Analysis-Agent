from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator

from app.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TraceRecord:
    trace_id: str
    spans: list[dict[str, Any]] = field(default_factory=list)

    def add_span(self, name: str, duration_ms: float, metadata: Dict[str, Any] | None = None) -> None:
        self.spans.append(
            {
                'name': name,
                'duration_ms': round(duration_ms, 2),
                'metadata': metadata or {},
            }
        )


def new_trace_id() -> str:
    return f"tr_{uuid.uuid4().hex[:12]}"


@contextmanager
def traced_step(trace: TraceRecord, step_name: str, **metadata: Any) -> Iterator[None]:
    start = time.perf_counter()
    logger.info('trace.start trace_id=%s step=%s metadata=%s', trace.trace_id, step_name, metadata)
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        trace.add_span(step_name, duration_ms, metadata)
        logger.info('trace.end trace_id=%s step=%s duration_ms=%.2f', trace.trace_id, step_name, duration_ms)
