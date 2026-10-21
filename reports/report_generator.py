
from datetime import datetime
import polars as pl


def generate_report(df: pl.DataFrame) -> str:
    """Generate a text report for an uploaded dataset."""

    missing = {
        column: df[column].null_count()
        for column in df.columns
    }

    if df.columns:
        empty_string_counts = {}
        for column in df.columns:
            if df[column].dtype == pl.String:
                empty_string_counts[column] = (
                    df[column]
                    .str.strip_chars()
                    .eq("")
                    .fill_null(False)
                    .sum()
                )

        for column, count in empty_string_counts.items():
            missing[column] += count

    total_missing = sum(missing.values())
    duplicate_rows = df.height - df.unique().height

    lines = [
        "AI DATA ANALYTICS AGENT",
        "AUTOMATED DATA QUALITY REPORT",
        "=" * 40,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "DATASET OVERVIEW",
        "-" * 40,
        f"Total rows: {df.height}",
        f"Total columns: {df.width}",
        f"Duplicate rows: {duplicate_rows}",
        f"Total missing values: {total_missing}",
        "",
        "MISSING VALUES BY COLUMN",
        "-" * 40,
    ]

    for column, count in missing.items():
        lines.append(f"{column}: {count}")

    lines.extend([
        "",
        "NUMERIC SUMMARY",
        "-" * 40,
    ])

    numeric_columns = [
        name
        for name, dtype in zip(df.columns, df.dtypes)
        if dtype.is_numeric()
    ]

    if numeric_columns:
        lines.append(df.select(numeric_columns).describe().write_csv())
    else:
        lines.append("No numeric columns found.")

    lines.extend([
        "",
        "END OF REPORT",
    ])

    return "\n".join(lines)
