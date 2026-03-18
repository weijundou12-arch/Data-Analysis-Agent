from __future__ import annotations

from pathlib import Path

TOOL_CONTRACT = {
    "name": "write_report",
    "goal": "Write a structured markdown report from analysis outputs.",
    "inputs": ["analysis artifacts"],
    "outputs": ["report_path"],
    "must_not_do": ["drop evidence or hide warnings"],
}


def write_report(output_dir: str, analysis_id: str, dataset_id: str, profile: dict, columns: dict, stats: dict, plot_paths: list[str], warnings: list[str]) -> str:
    path = Path(output_dir) / "report.md"
    numeric_cols = stats.get("numeric_columns", [])
    lines = [
        f"# Data Analysis Report: {analysis_id}",
        "",
        f"- Dataset ID: {dataset_id}",
        f"- Rows: {profile.get('rows')}",
        f"- Columns: {profile.get('columns')}",
        f"- Duplicate rows: {profile.get('duplicate_rows')}",
        "",
        "## Dataset Profile",
        "",
    ]

    for col in profile.get("column_names", []):
        dtype = profile.get("dtypes", {}).get(col, "unknown")
        missing = profile.get("missing_values", {}).get(col, 0)
        lines.append(f"- {col}: dtype={dtype}, missing={missing}")

    lines.extend(["", "## Numeric Columns", ""])
    if numeric_cols:
        for col in numeric_cols:
            desc = stats.get("describe", {}).get(col, {})
            lines.append(
                f"- {col}: mean={desc.get('mean')}, std={desc.get('std')}, min={desc.get('min')}, max={desc.get('max')}"
            )
    else:
        lines.append("- No numeric columns detected.")

    lines.extend(["", "## Column Summaries", ""])
    for col, item in columns.items():
        lines.append(f"- {col}: {item}")

    lines.extend(["", "## Generated Plots", ""])
    if plot_paths:
        for p in plot_paths:
            lines.append(f"- {Path(p).name}")
    else:
        lines.append("- No plots generated.")

    lines.extend(["", "## Warnings", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No warnings recorded.")

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
