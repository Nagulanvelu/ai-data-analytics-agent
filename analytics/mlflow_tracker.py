
import mlflow
import polars as pl

from reports.report_generator import generate_report


def track_dataset_analysis(df: pl.DataFrame) -> str:
    """Track dataset quality metrics and report using MLflow."""

    mlflow.set_experiment("AI Data Analytics Agent")

    with mlflow.start_run() as run:
        rows = df.height
        columns = df.width
        total_cells = rows * columns

        # Calculate missing and blank values.
        missing_count = 0

        for column in df.columns:
            missing_count += df[column].null_count()

            if df[column].dtype == pl.String:
                missing_count += (
                    df[column]
                    .str.strip_chars()
                    .eq("")
                    .fill_null(False)
                    .sum()
                )

        duplicate_count = rows - df.unique().height

        missing_percentage = (
            missing_count / total_cells * 100
            if total_cells > 0
            else 0.0
        )

        duplicate_percentage = (
            duplicate_count / rows * 100
            if rows > 0
            else 0.0
        )

        numeric_columns = [
            name
            for name, dtype in zip(df.columns, df.dtypes)
            if dtype.is_numeric()
        ]

        categorical_columns = [
            name
            for name, dtype in zip(df.columns, df.dtypes)
            if dtype == pl.String
        ]

        quality_score = max(
            0.0,
            min(
                100.0,
                100.0
                - missing_percentage
                - (duplicate_percentage * 10),
            ),
        )

        # Log parameters.
        mlflow.log_param("dataset_rows", rows)
        mlflow.log_param("dataset_columns", columns)
        mlflow.log_param("numeric_columns", len(numeric_columns))
        mlflow.log_param("categorical_columns", len(categorical_columns))

        # Log metrics.
        mlflow.log_metric("missing_values", missing_count)
        mlflow.log_metric("missing_percentage", missing_percentage)
        mlflow.log_metric("duplicate_rows", duplicate_count)
        mlflow.log_metric("duplicate_percentage", duplicate_percentage)
        mlflow.log_metric("data_quality_score", quality_score)

        # Generate and log the report.
        report_text = generate_report(df)

        with open(
            "data_quality_report.txt",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(report_text)

        mlflow.log_artifact("data_quality_report.txt")

        return run.info.run_id
