
import polars as pl


def get_dataset_overview(df: pl.DataFrame) -> dict:
    """Return a summary of the dataset."""
    return {
        "rows": df.height,
        "columns": df.width,
        "column_names": df.columns,
        "duplicate_rows": df.height - df.unique().height,
    }


def get_missing_values(df: pl.DataFrame) -> pl.DataFrame:
    """Count missing values in every column."""
    return pl.DataFrame({
        "Column": df.columns,
        "Missing Values": [
            df[column].null_count() for column in df.columns
        ],
    })


def get_numeric_summary(df: pl.DataFrame) -> pl.DataFrame:
    """Summarize numeric columns."""
    numeric_columns = [
        name
        for name, dtype in zip(df.columns, df.dtypes)
        if dtype.is_numeric()
    ]

    if not numeric_columns:
        return pl.DataFrame({
            "Message": ["No numeric columns found."]
        })

    return df.select(numeric_columns).describe()


def find_column(df: pl.DataFrame, question: str) -> pl.DataFrame:
    """Return columns whose names match words in the question."""
    matches = [
        column for column in df.columns
        if column.lower() in question.lower()
    ]

    if not matches:
        return pl.DataFrame({
            "Message": [
                "No matching column name found. Check the spelling."
            ]
        })

    return df.select(matches).head(10)
