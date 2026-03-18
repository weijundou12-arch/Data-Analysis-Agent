from __future__ import annotations

from threading import Lock
from typing import Any


class CacheService:
    def __init__(self) -> None:
        self._datasets: dict[str, dict[str, Any]] = {}
        self._analyses: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def set_dataset(self, dataset_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._datasets[dataset_id] = payload

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._datasets.get(dataset_id)

    def set_analysis(self, analysis_id: str, payload: dict[str, Any]) -> None:
        with self._lock:
            self._analyses[analysis_id] = payload

    def get_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._analyses.get(analysis_id)

    def reset(self) -> None:
        with self._lock:
            self._datasets.clear()
            self._analyses.clear()


cache = CacheService()
