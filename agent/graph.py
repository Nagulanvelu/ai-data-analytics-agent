
from agent.tools import (
    get_dataset_overview,
    get_missing_values,
    get_numeric_summary,
    find_column,
)


def answer_question(df, question: str):
    """Choose an analytics tool based on a natural-language question."""
    q = question.lower().strip()

    if any(word in q for word in [
        "missing", "null", "empty", "data quality"
    ]):
        return {
            "tool": "Missing Values Analysis",
            "result": get_missing_values(df),
        }

    if any(word in q for word in [
        "average", "mean", "median", "statistics",
        "numeric", "summary", "maximum", "minimum"
    ]):
        return {
            "tool": "Numeric Summary",
            "result": get_numeric_summary(df),
        }

    if any(word in q for word in [
        "overview", "dataset", "how many rows",
        "how many columns", "duplicates", "describe"
    ]):
        return {
            "tool": "Dataset Overview",
            "result": get_dataset_overview(df),
        }

    return {
        "tool": "Column Search",
        "result": find_column(df, question),
    }
