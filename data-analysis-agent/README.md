# Data Analysis Agent

Tool-driven FastAPI service for CSV/tabular data analysis and report generation.

## Features

- Upload CSV or Excel files.
- Run a single-agent analysis workflow with explicit state tracking.
- Generate dataset profiling, column summaries, descriptive statistics, and basic plots.
- Export a structured markdown report and artifact paths.
- Capture trace spans, warnings, retries, and output files for each run.
- Ship with Docker and pytest.

## Repository Structure

```text
data-analysis-agent/
├─ app/
│  ├─ main.py
│  ├─ schemas/
│  │  ├─ upload.py
│  │  ├─ analysis.py
│  │  └─ report.py
│  ├─ api/
│  │  ├─ routes_upload.py
│  │  ├─ routes_analyze.py
│  │  └─ routes_export.py
│  ├─ agent/
│  │  ├─ orchestrator.py
│  │  ├─ state.py
│  │  └─ tool_registry.py
│  ├─ tools/
│  │  ├─ profile_dataset.py
│  │  ├─ summarize_columns.py
│  │  ├─ generate_plots.py
│  │  ├─ run_basic_stats.py
│  │  └─ write_report.py
│  ├─ services/
│  │  ├─ dataframe_service.py
│  │  ├─ report_service.py
│  │  └─ cache_service.py
│  └─ observability/
│     ├─ logging.py
│     └─ tracing.py
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## How It Works

1. `POST /upload` saves a tabular file and records dataset metadata.
2. `POST /analyze` creates an agent state and runs the workflow.
3. The orchestrator executes tool contracts in order:
   - `profile_dataset`
   - `summarize_columns`
   - `run_basic_stats`
   - `generate_plots`
   - `write_report`
4. Results, artifacts, warnings, retries, and trace spans are cached per analysis.
5. `GET /export/{analysis_id}` returns the final report payload.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit the docs at `http://127.0.0.1:8000/docs`.

## Example API Flow

### 1. Upload a dataset

```bash
curl -X POST http://127.0.0.1:8000/upload   -F "file=@sample.csv"
```

### 2. Run analysis

```bash
curl -X POST http://127.0.0.1:8000/analyze   -H "Content-Type: application/json"   -d '{
    "dataset_id": "ds_xxxxx",
    "include_plots": true,
    "max_plots": 2,
    "run_in_background": false
  }'
```

### 3. Export the report

```bash
curl http://127.0.0.1:8000/export/an_xxxxx
```

## Testing

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```

## Notes

- The service keeps runtime data under `DATA_ANALYSIS_AGENT_HOME`.
- The cache layer is in-memory for simplicity.
- The plotting tool retries once if plot generation fails.
- The tracing layer records step-level durations and metadata for each run.
