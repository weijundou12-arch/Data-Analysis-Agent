import os

os.environ["DATA_ANALYSIS_AGENT_HOME"] = "/tmp/data-analysis-agent-tests"

from fastapi.testclient import TestClient

from app.main import app
from app.services.cache_service import cache

client = TestClient(app)


def setup_function():
    cache.reset()


def test_upload_analyze_and_export_flow(tmp_path):
    csv_content = """age,score,group
21,88,a
30,92,a
33,95,b
"""
    upload_response = client.post(
        "/upload",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert upload_response.status_code == 200
    dataset_id = upload_response.json()["dataset_id"]

    analyze_response = client.post(
        "/analyze",
        json={"dataset_id": dataset_id, "include_plots": True, "max_plots": 2, "run_in_background": False},
    )
    assert analyze_response.status_code == 200
    payload = analyze_response.json()
    assert payload["status"] == "completed"
    assert payload["report_path"].endswith("report.md")

    export_response = client.get(f"/export/{payload['analysis_id']}")
    assert export_response.status_code == 200
    export_payload = export_response.json()
    assert export_payload["analysis_id"] == payload["analysis_id"]
    assert export_payload["summary"]["profile"]["rows"] == 3


def test_background_analysis_returns_pending():
    csv_content = """x,y
1,2
3,4
"""
    upload_response = client.post("/upload", files={"file": ("sample.csv", csv_content, "text/csv")})
    dataset_id = upload_response.json()["dataset_id"]

    analyze_response = client.post(
        "/analyze",
        json={"dataset_id": dataset_id, "include_plots": False, "run_in_background": True},
    )
    assert analyze_response.status_code == 200
    assert analyze_response.json()["status"] == "pending"
