
from datetime import datetime
import polars as pl


def generate_report(df: pl.DataFrame) -> str:
    """Generate a detailed text report for an uploaded dataset."""

    total_rows = df.height
    total_columns = df.width

    # Calculate missing values, including blank strings.
    missing = {}

    for column in df.columns:
        null_count = df[column].null_count()
        blank_count = 0

        if df[column].dtype == pl.String:
            blank_count = (
                df[column]
                .str.strip_chars()
                .eq("")
                .fill_null(False)
                .sum()
            )

        missing[column] = null_count + blank_count

    total_missing = sum(missing.values())
    total_cells = total_rows * total_columns

    missing_percentage = (
        (total_missing / total_cells) * 100
        if total_cells > 0
        else 0.0
    )

    # Count duplicate rows.
    duplicate_rows = total_rows - df.unique().height

    # Calculate a simple data quality score.
    quality_score = max(0.0, 100.0 - missing_percentage)

    if duplicate_rows > 0 and total_rows > 0:
        quality_score -= (duplicate_rows / total_rows) * 10

    quality_score = max(0.0, min(100.0, quality_score))

    # Identify numeric columns.
    numeric_columns = [
        name
        for name, dtype in zip(df.columns, df.dtypes)
        if dtype.is_numeric()
    ]

    lines = [
        "AI DATA ANALYTICS AGENT",
        "AUTOMATED DATA QUALITY REPORT",
        "=" * 55,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "1. DATASET OVERVIEW",
        "-" * 55,
        f"Total rows: {total_rows:,}",
        f"Total columns: {total_columns:,}",
        f"Total cells: {total_cells:,}",
        f"Duplicate rows: {duplicate_rows:,}",
        f"Total missing/blank values: {total_missing:,}",
        f"Missing-value percentage: {missing_percentage:.2f}%",
        f"Estimated data quality score: {quality_score:.2f}/100",
        "",
        "2. MISSING VALUES BY COLUMN",
        "-" * 55,
    ]

    if missing:
        for column, count in missing.items():
            percentage = (
                (count / total_rows) * 100
                if total_rows > 0
                else 0.0
            )
            lines.append(
                f"{column}: {count:,} ({percentage:.2f}%)"
            )
    else:
        lines.append("No columns found.")

    lines.extend([
        "",
        "3. NUMERICAL STATISTICS",
        "-" * 55,
    ])

    if numeric_columns:
        summary = df.select(numeric_columns).describe()
        lines.append(summary.write_csv())
    else:
        lines.append("No numeric columns found.")

    lines.extend([
        "",
        "4. DATA QUALITY OBSERVATIONS",
        "-" * 55,
    ])

    if total_missing == 0:
        lines.append("No missing or blank values detected.")
    else:
        lines.append(
            f"Review {total_missing:,} missing or blank values "
            "before analysis."
        )

    if duplicate_rows == 0:
        lines.append("No duplicate rows detected.")
    else:
        lines.append(
            f"{duplicate_rows:,} duplicate rows detected. "
            "Review them before removing any records."
        )

    if not numeric_columns:
        lines.append(
            "No numeric columns are available for numerical analysis."
        )

    lines.extend([
        "",
        "Note: The data quality score is a simple estimate based on "
        "missing values and duplicate rows, not a certified metric.",
        "",
        "END OF REPORT",
        "=" * 55,
    ])

    return "\n".join(lines)
