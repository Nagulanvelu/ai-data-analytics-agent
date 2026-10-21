
import duckdb
import polars as pl


def run_sql_query(df: pl.DataFrame, query: str) -> pl.DataFrame:
    """
    Run a read-only SQL query against the uploaded dataset.
    Access the dataset using the table name 'data'.
    """
    if not query.strip():
        raise ValueError("Please enter a SQL query.")

    connection = duckdb.connect(":memory:")

    try:
        connection.register("data", df.to_arrow())

        # Permit only read-only SELECT queries.
        normalized_query = query.strip().rstrip(";")
        if not normalized_query.lower().startswith("select "):
            raise ValueError("Only SELECT queries are allowed.")

        result = connection.execute(normalized_query).pl()
        return result

    finally:
        connection.close()
