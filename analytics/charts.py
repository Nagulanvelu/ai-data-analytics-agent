
import polars as pl
import plotly.express as px


def create_missing_values_chart(df: pl.DataFrame):
    """Create a chart of missing values for each column."""

    counts = []

    for column in df.columns:
        count = df[column].null_count()

        if df[column].dtype == pl.String:
            count += (
                df[column]
                .str.strip_chars()
                .eq("")
                .fill_null(False)
                .sum()
            )

        counts.append(count)

    chart_df = pl.DataFrame({
        "Column": df.columns,
        "Missing Values": counts,
    }).filter(pl.col("Missing Values") > 0)

    if chart_df.is_empty():
        return None

    return px.bar(
        chart_df.to_pandas(),
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
        text="Missing Values",
    )
