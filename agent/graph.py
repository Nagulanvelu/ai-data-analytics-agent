
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



import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

ALLOWED_TOOLS = {
    "overview": "Dataset Overview",
    "missing": "Missing Values Analysis",
    "numeric": "Numeric Summary",
    "column_search": "Column Search",
}


class AgentState(TypedDict):
    df: object
    question: str
    selected_tool: str
    result: object
    explanation: str


def choose_tool(state: AgentState) -> dict:
    """Ask Groq which existing analytics operation best fits."""
    from langchain_core.messages import SystemMessage, HumanMessage

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your local .env file."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    response = llm.invoke([
        SystemMessage(content=(
            "You route questions about CSV datasets to exactly one tool. "
            "Return only valid JSON with keys 'tool' and 'explanation'. "
            "Allowed tool values: overview, missing, numeric, column_search. "
            "Use missing for nulls, blanks, or data quality questions. "
            "Use numeric for statistics, averages, minimums, or maximums. "
            "Use overview for dataset size, columns, or duplicates. "
            "Use column_search when a question asks to inspect a column. "
            "Never invent data or execute SQL."
        )),
        HumanMessage(content=(
            f"Dataset columns: {state['df'].columns}\n"
            f"User question: {state['question']}"
        )),
    ])

    try:
        decision = json.loads(response.content)
        selected = decision.get("tool", "")
        if selected not in ALLOWED_TOOLS:
            raise ValueError("Unknown tool")
        explanation = str(decision.get("explanation", ""))
    except (ValueError, TypeError, json.JSONDecodeError):
        # Use the existing rule-based router if the response is malformed.
        fallback = answer_question(state["df"], state["question"])
        selected = {
            "Dataset Overview": "overview",
            "Missing Values Analysis": "missing",
            "Numeric Summary": "numeric",
            "Column Search": "column_search",
        }.get(fallback["tool"], "overview")
        explanation = "Used the rule-based fallback."

    return {
        "selected_tool": selected,
        "explanation": explanation,
    }


def execute_tool(state: AgentState) -> dict:
    """Run the selected Python analytics function on the real dataset."""
    from agent.tools import (
        get_dataset_overview,
        get_missing_values,
        get_numeric_summary,
        find_column,
    )

    df = state["df"]
    question = state["question"]

    operations = {
        "overview": lambda: get_dataset_overview(df),
        "missing": lambda: get_missing_values(df),
        "numeric": lambda: get_numeric_summary(df),
        "column_search": lambda: find_column(df, question),
    }

    result = operations[state["selected_tool"]]()
    return {"result": result}


workflow = StateGraph(AgentState)
workflow.add_node("choose_tool", choose_tool)
workflow.add_node("execute_tool", execute_tool)
workflow.add_edge(START, "choose_tool")
workflow.add_edge("choose_tool", "execute_tool")
workflow.add_edge("execute_tool", END)

groq_agent = workflow.compile()



def answer_question_with_groq(df, question: str) -> dict:
    """Use Groq when available; fall back to rule-based analytics."""
    try:
        state = groq_agent.invoke({
            "df": df,
            "question": question,
            "selected_tool": "",
            "result": None,
            "explanation": "",
        })

        return {
            "tool": ALLOWED_TOOLS[state["selected_tool"]],
            "result": state["result"],
            "explanation": state.get(
                "explanation",
                "Selected a tool using Groq.",
            ),
            "mode": "groq",
        }

    except Exception as exc:
        try:
            fallback = answer_question(df, question)

            return {
                "tool": fallback["tool"],
                "result": fallback["result"],
                "explanation": (
                    "Groq was unavailable; the rule-based fallback was used. "
                    f"Reason: {type(exc).__name__}"
                    
                ),
                "mode": "fallback",
            }
        except Exception as fallback_exc:
            raise RuntimeError(
                "Both Groq and rule-based analytics failed."
            ) from fallback_exc
