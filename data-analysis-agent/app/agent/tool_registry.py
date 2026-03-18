from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from app.tools.generate_plots import TOOL_CONTRACT as PLOT_CONTRACT, generate_plots
from app.tools.profile_dataset import TOOL_CONTRACT as PROFILE_CONTRACT, profile_dataset
from app.tools.run_basic_stats import TOOL_CONTRACT as STATS_CONTRACT, run_basic_stats
from app.tools.summarize_columns import TOOL_CONTRACT as SUMMARY_CONTRACT, summarize_columns
from app.tools.write_report import TOOL_CONTRACT as REPORT_CONTRACT, write_report


@dataclass
class ToolSpec:
    name: str
    fn: Callable
    contract: dict


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}
        self.register('profile_dataset', profile_dataset, PROFILE_CONTRACT)
        self.register('summarize_columns', summarize_columns, SUMMARY_CONTRACT)
        self.register('run_basic_stats', run_basic_stats, STATS_CONTRACT)
        self.register('generate_plots', generate_plots, PLOT_CONTRACT)
        self.register('write_report', write_report, REPORT_CONTRACT)

    def register(self, name: str, fn: Callable, contract: dict) -> None:
        self._tools[name] = ToolSpec(name=name, fn=fn, contract=contract)

    def get(self, name: str) -> ToolSpec:
        return self._tools[name]


tool_registry = ToolRegistry()
