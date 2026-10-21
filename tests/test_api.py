
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_csv_missing_values():
    csv_content = (
        b"Name,Score\n"
        b"Alice,90\n"
        b"Bob,\n"
    )

    response = client.post(
        "/analyze",
        params={"question": "Which columns have missing values?"},
        files={
            "file": (
                "sample.csv",
                csv_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()
    assert result["rows"] == 2
    assert result["columns"] == 2
    assert result["selected_tool"] == "Missing Values Analysis"


def test_analyze_rejects_non_csv():
    response = client.post(
        "/analyze",
        files={
            "file": (
                "sample.txt",
                b"not a csv",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_report_endpoint():
    csv_content = b"Name,Score\nAlice,90\nBob,80\n"

    response = client.post(
        "/report",
        files={
            "file": (
                "sample.csv",
                csv_content,
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert "DATASET OVERVIEW" in response.text
    assert "Total rows: 2" in response.text
