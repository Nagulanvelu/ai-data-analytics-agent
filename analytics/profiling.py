
import polars as pl


def profile_csv(file):
    df = pl.read_csv(file, infer_schema_length=10000)

    summary = {
        "rows": df.height,
        "columns": df.width,
        "duplicate_rows": df.height - df.unique().height,
        "missing_values": {
            column: df[column].null_count()
            for column in df.columns
        },
        "column_names": df.columns,
    }

    return df, summary
