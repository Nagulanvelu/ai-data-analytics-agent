
from unittest.mock import patch

import polars as pl

from agent.graph import answer_question_with_groq


def sample_dataset():
    return pl.DataFrame({
        "Name": ["Alice", "Bob"],
        "Score": [90, None],
    })


def test_groq_success():
    df = sample_dataset()

    mock_state = {
        "selected_tool": "missing",
        "result": pl.DataFrame({
            "Column": ["Name", "Score"],
            "Missing Values": [0, 1],
        }),
        "explanation": "Checking missing values.",
    }

    with patch("agent.graph.groq_agent.invoke", return_value=mock_state):
        response = answer_question_with_groq(
            df,
            "Which columns have missing values?",
        )

    assert response["tool"] == "Missing Values Analysis"
    assert response["mode"] == "groq"
    assert response["result"]["Missing Values"][1] == 1


def test_groq_failure_uses_fallback():
    df = sample_dataset()

    with patch(
        "agent.graph.groq_agent.invoke",
        side_effect=RuntimeError("Simulated Groq outage"),
    ):
        response = answer_question_with_groq(
            df,
            "Which columns have missing values?",
        )

    assert response["mode"] == "fallback"
    assert response["tool"] == "Missing Values Analysis"
    assert "fallback" in response["explanation"].lower()
