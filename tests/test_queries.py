
import polars as pl
import pytest

from analytics.queries import run_sql_query


def test_sql_count_query():
    df = pl.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Score": [90, 80, 70],
    })

    result = run_sql_query(
        df,
        "SELECT COUNT(*) AS total FROM data",
    )

    assert result["total"][0] == 3


def test_sql_filter_query():
    df = pl.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Score": [90, 80, 70],
    })

    result = run_sql_query(
        df,
        "SELECT Name FROM data WHERE Score > 75",
    )

    assert result.height == 2


def test_sql_rejects_non_select_query():
    df = pl.DataFrame({"Score": [90, 80]})

    with pytest.raises(ValueError):
        run_sql_query(df, "DELETE FROM data")
