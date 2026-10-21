
import mlflow
import pandas as pd


def get_experiment_runs() -> pd.DataFrame:
    """Return MLflow experiment runs as a comparison table."""

    experiment = mlflow.get_experiment_by_name(
        "AI Data Analytics Agent"
    )

    if experiment is None:
        return pd.DataFrame()

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
    )

    if runs.empty:
        return runs

    columns = {
        "run_id": "Run ID",
        "start_time": "Started",
        "params.dataset_rows": "Rows",
        "params.dataset_columns": "Columns",
        "metrics.data_quality_score": "Quality Score",
        "metrics.missing_values": "Missing Values",
        "metrics.duplicate_rows": "Duplicate Rows",
        "metrics.missing_percentage": "Missing %",
        "metrics.duplicate_percentage": "Duplicate %",
    }

    available = {
        key: value
        for key, value in columns.items()
        if key in runs.columns
    }

    return runs[list(available)].rename(columns=available)
