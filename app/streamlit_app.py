
import io

import mlflow
import plotly.express as px
import polars as pl
import streamlit as st

from analytics.profiling import profile_csv
from analytics.queries import run_sql_query
from analytics.charts import create_missing_values_chart
from analytics.mlflow_tracker import track_dataset_analysis
from agent.graph import answer_question_with_groq
from reports.report_generator import generate_report

from analytics.mlflow_dashboard import get_experiment_runs


st.set_page_config(
    page_title="AI Data Analytics Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 AI-Powered Data Analytics Agent")
st.write(
    "Upload a CSV file to explore your data, "
    "check data quality, ask questions, and generate charts."
)

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        df, summary = profile_csv(io.BytesIO(file_bytes))

        st.success("Dataset loaded successfully!")

        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", f"{summary['rows']:,}")
        col2.metric("Columns", summary["columns"])
        col3.metric("Duplicate rows", summary["duplicate_rows"])

        st.subheader("📋 Data Preview")
        st.dataframe(df.to_pandas(), use_container_width=True)

        st.subheader("🔍 Missing Values")
        missing_df = pl.DataFrame({
            "Column": list(summary["missing_values"].keys()),
            "Missing Values": list(summary["missing_values"].values()),
        })
        st.dataframe(missing_df.to_pandas(), use_container_width=True)

        st.subheader("📈 Column Statistics")
        st.dataframe(df.describe().to_pandas(), use_container_width=True)

        numeric_columns = [
            name
            for name, dtype in zip(df.columns, df.dtypes)
            if dtype.is_numeric()
        ]

        if numeric_columns:
            st.subheader("📊 Interactive Chart")
            selected_column = st.selectbox(
                "Choose a numeric column",
                numeric_columns,
            )

            chart_df = (
                df.select(selected_column)
                .drop_nulls()
                .to_pandas()
            )

            fig = px.histogram(
                chart_df,
                x=selected_column,
                title=f"Distribution of {selected_column}",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("🔎 Ask Your Data with SQL")
        st.caption("Use the table name `data` to query your uploaded CSV.")

        sql_query = st.text_area(
            "SQL Query",
            value="SELECT * FROM data LIMIT 10",
            height=120,
        )

        if st.button("Run SQL Query"):
            try:
                query_result = run_sql_query(df, sql_query)
                st.success(
                    f"Query completed: {query_result.height} rows returned."
                )
                st.dataframe(
                    query_result.to_pandas(),
                    use_container_width=True,
                )
                st.download_button(
                    "Download Query Results",
                    data=query_result.write_csv(),
                    file_name="sql_query_results.csv",
                    mime="text/csv",
                )
            except Exception as exc:
                st.error(f"SQL query failed: {exc}")

        st.divider()
        st.subheader("🤖 Ask the Analytics Agent")

        user_question = st.text_input(
            "Ask a question about your dataset",
            placeholder="Example: Which columns have missing values?",
        )

        if st.button("Ask Agent"):
            if not user_question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner("Analyzing your question..."):
                        response = answer_question_with_groq(
                            df,
                            user_question,
                        )

                    st.write(f"**Selected tool:** {response['tool']}")
                    st.caption(
                        response.get("explanation", "Analysis completed.")
                    )

                    if response.get("mode") == "groq":
                        st.success("Groq-powered agent used successfully.")
                    else:
                        st.warning(
                            "Groq was unavailable. Rule-based fallback used."
                        )

                    result = response["result"]

                    if isinstance(result, pl.DataFrame):
                        st.dataframe(
                            result.to_pandas(),
                            use_container_width=True,
                        )
                    else:
                        st.json(result)

                except Exception as exc:
                    st.error(f"Agent error: {exc}")

        st.divider()
        st.subheader("📊 Data Quality Visualization")

        missing_fig = create_missing_values_chart(df)

        if missing_fig is not None:
            st.plotly_chart(missing_fig, use_container_width=True)
        else:
            st.success("No missing values detected.")

        st.divider()
        st.subheader("🧪 MLflow Experiment Tracking")

        st.write(
            "Record dataset quality metrics and save the generated "
            "data quality report as an MLflow artifact."
        )

        if st.button("Track Analysis with MLflow"):
            try:
                with st.spinner("Logging experiment to MLflow..."):
                    run_id = track_dataset_analysis(df)

                st.success("Analysis tracked successfully!")
                st.write("**MLflow Run ID**")
                st.code(run_id, language="text")

            except Exception as exc:
                st.error(f"MLflow tracking failed: {exc}")

        # Download analyzed CSV
        st.download_button(
            "📊 Download Analyzed CSV",
            data=df.write_csv(),
            file_name="analyzed_data.csv",
            mime="text/csv",
        )

        # Download data quality report
        report_text = generate_report(df)

        st.download_button(
            "📄 Download Data Quality Report",
            data=report_text,
            file_name="data_quality_report.txt",
            mime="text/plain",
        )
        
        st.divider()
        st.subheader("📈 MLflow Experiment Comparison")

        if st.button("Refresh Experiment Runs"):
            try:
                runs_df = get_experiment_runs()

                if runs_df.empty:
                    st.info("No MLflow experiment runs found yet.")
                else:
                    st.dataframe(
                        runs_df,
                        use_container_width=True,
                    )

                    if "Quality Score" in runs_df.columns:
                        chart_df = runs_df.dropna(
                            subset=["Quality Score"]
                        )

                        if not chart_df.empty:
                            st.bar_chart(
                                chart_df.set_index("Run ID")[
                                    "Quality Score"
                                ]
                            )

            except Exception as exc:
                st.error(
                    f"Could not load MLflow runs: {exc}"
                )


    except Exception as exc:
        st.error(f"Could not analyze this file: {exc}")
