
import polars as pl

from analytics.mlflow_tracker import track_dataset_analysis
from reports.report_generator import generate_report


def test_report_contains_dataset_overview():
    df = pl.DataFrame({
        "Name": ["A", "B", "A"],
        "Score": [90, None, 90],
    })

    report = generate_report(df)

    assert "Total rows: 3" in report
    assert "Total columns: 2" in report
    assert "Duplicate rows: 1" in report
    assert "Total missing/blank values: 1" in report


def test_mlflow_tracker_returns_run_id():
    df = pl.DataFrame({
        "Name": ["A", "B"],
        "Score": [90, 80],
    })

    run_id = track_dataset_analysis(df)

    assert isinstance(run_id, str)
    assert len(run_id) > 0
