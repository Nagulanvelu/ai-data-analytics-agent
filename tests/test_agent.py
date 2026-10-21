
import polars as pl

from agent.graph import answer_question
from reports.report_generator import generate_report


def sample_dataset():
    return pl.DataFrame({
        "Name": ["A", "B", "C"],
        "Score": [80, 90, 70],
        "City": ["Chennai", None, "Mumbai"],
    })


def test_missing_values_analysis():
    df = sample_dataset()
    response = answer_question(df, "Which columns have missing values?")

    assert response["tool"] == "Missing Values Analysis"
    result = response["result"]

    city_missing = result.filter(
        pl.col("Column") == "City"
    )["Missing Values"][0]

    assert city_missing == 1


def test_dataset_overview():
    df = sample_dataset()
    response = answer_question(df, "Show dataset overview")

    assert response["tool"] == "Dataset Overview"
    assert response["result"]["rows"] == 3
    assert response["result"]["columns"] == 3


def test_report_generation():
    df = sample_dataset()
    report = generate_report(df)

    assert "DATASET OVERVIEW" in report
    assert "Total rows: 3" in report
    assert "City: 1" in report
