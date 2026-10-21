

import io

import mlflow
import plotly.express as px
import polars as pl
import streamlit as st

from analytics.profiling import profile_csv
from analytics.queries import run_sql_query
from analytics.charts import create_missing_values_chart
from analytics.mlflow_tracker import track_dataset_analysis
from analytics.mlflow_dashboard import get_experiment_runs
from agent.graph import answer_question_with_groq
from reports.report_generator import generate_report



st.set_page_config(
    page_title="AI Data Analytics Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM DESIGN — LIGHT, COLORFUL, HIGH-CONTRAST
# ============================================================

st.markdown("""
<style>
/* Overall background */
.stApp {
    background: linear-gradient(135deg, #eef3ff 0%, #faf5ff 100%);
    color: #172554;
}

[data-testid="stHeader"] {
    background: rgba(245, 247, 255, 0.92);
}

/* Main content spacing */
.block-container {
    max-width: 1500px;
    padding: 1.5rem 2rem 3rem 2rem;
}

/* Gradient hero */
.hero {
    background: linear-gradient(110deg, #293bb5 0%, #4f46e5 52%, #d946ef 100%);
    padding: 30px 34px;
    border-radius: 22px;
    color: #ffffff;
    margin-bottom: 22px;
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.19);
}
.hero h1 {
    color: #ffffff !important;
    font-size: clamp(1.8rem, 3vw, 2.7rem);
    font-weight: 800;
    margin: 0;
}
.hero p {
    color: #ffffff !important;
    font-size: 1.05rem;
    margin: 9px 0 0;
}

/* Technology chips */
.chip {
    display: inline-block;
    padding: 7px 13px;
    margin: 18px 7px 0 0;
    border: 1px solid rgba(255,255,255,.4);
    background: rgba(255,255,255,.15);
    border-radius: 30px;
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
}

/* Upload panel */
.upload-panel {
    background: #ffffff;
    border: 1px solid #dbe4ff;
    border-radius: 19px;
    padding: 20px 24px 12px;
    margin-bottom: 18px;
    box-shadow: 0 5px 20px rgba(48, 65, 130, .06);
}

/* Headings */
h1, h2, h3, h4 {
    color: #172554 !important;
    font-weight: 750;
}
p, label, li {
    color: #334155;
}
.section-caption {
    color: #52658c;
    font-size: 0.98rem;
}

/* Navigation buttons from horizontal radio */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    padding: 8px 0 15px;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 13px;
    padding: 10px 16px;
    margin: 0;
    box-shadow: 0 4px 12px rgba(48, 65, 130, .05);
    transition: all .18s ease;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    border-color: #818cf8;
    background: #eef2ff;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(105deg, #3b5bdb, #8b5cf6);
    border-color: transparent;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) * {
    color: #ffffff !important;
}

/* KPI cards */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e0e7ff;
    border-radius: 17px;
    padding: 18px 18px;
    min-height: 112px;
    box-shadow: 0 5px 18px rgba(48, 65, 130, .06);
}
[data-testid="stMetricLabel"] {
    color: #52658c !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #243da8 !important;
    font-weight: 800;
}

/* White content panels */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: #ffffff;
    border: 1px solid #dce5fa;
    border-radius: 13px;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #ffffff;
    color: #172554;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #ffffff;
    border-radius: 10px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(105deg, #4056d6, #8739e8);
    color: #ffffff !important;
    border: none;
    border-radius: 10px;
    font-weight: 650;
    padding: .55rem 1rem;
    transition: all .18s ease;
}
.stButton > button:hover {
    background: linear-gradient(105deg, #293bb5, #7028c9);
    box-shadow: 0 5px 15px rgba(79, 70, 229, .2);
    transform: translateY(-1px);
}
.stDownloadButton > button {
    background: #eef2ff;
    color: #3730a3 !important;
    border: 1px solid #c7d2fe;
    border-radius: 10px;
    font-weight: 650;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1px dashed #8b9cff;
    border-radius: 14px;
    padding: 12px;
}
[data-testid="stFileUploaderDropzone"] {
    background: #f8faff;
    border: none;
}
[data-testid="stFileUploaderDropzone"] * {
    color: #243b80 !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #5b3df5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
}

/* Alerts and separators */
hr {
    border-color: #dce5fa;
}
[data-testid="stAlert"] {
    border-radius: 12px;
}
.footer {
    color: #64748b;
    text-align: center;
    font-size: .85rem;
    padding: 24px 0 5px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>📊 AI Data Analytics Agent</h1>
    <p>Explore data, discover quality issues, run analytics, and track experiments.</p>
    <span class="chip">🐍 Python</span>
    <span class="chip">⚡ Polars</span>
    <span class="chip">🗃️ DuckDB</span>
    <span class="chip">🤖 Groq</span>
    <span class="chip">📈 MLflow</span>
    <span class="chip">🎨 Streamlit</span>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CSV UPLOAD — MAIN PAGE, NO SIDEBAR
# ============================================================

st.markdown("""
<div class="upload-panel">
    <h3>📂 Upload your CSV file</h3>
    <p class="section-caption">
        Drag and drop your dataset here, or browse your computer.
        CSV files only.
    </p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    key="main_csv_upload",
    label_visibility="collapsed",
)


# ============================================================
# HORIZONTAL NAVIGATION
# ============================================================

page = st.radio(
    "Dashboard navigation",
    [
        "🏠 Overview",
        "🔎 Data Explorer",
        "🛡️ Data Quality",
        "🗃️ SQL Lab",
        "🤖 AI Assistant",
        "📈 MLflow Tracking",
        "🧪 Experiments",
        "📄 Reports",
    ],
    horizontal=True,
    label_visibility="collapsed",
)


# ============================================================
# LOAD DATASET
# ============================================================

df = None
summary = None

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()

        # Cache the parsed dataset across navigation reruns.
        signature = (
            uploaded_file.name,
            len(file_bytes),
            hash(file_bytes),
        )

        if st.session_state.get("dataset_signature") != signature:
            parsed_df, parsed_summary = profile_csv(
                io.BytesIO(file_bytes)
            )
            st.session_state["dataset_df"] = parsed_df
            st.session_state["dataset_summary"] = parsed_summary
            st.session_state["dataset_signature"] = signature

        df = st.session_state["dataset_df"]
        summary = st.session_state["dataset_summary"]

    except Exception as exc:
        st.error(f"Could not analyze this file: {exc}")
        st.stop()


def require_dataset():
    if df is None:
        st.info("📂 Upload a CSV using the upload box above to get started.")
        st.stop()


def get_numeric_columns():
    return [
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
        height=140,
    )

    if st.button("▶ Run SQL Query"):
        try:
            query_result = run_sql_query(df, sql_query)

            st.success(
                f"Query completed: {query_result.height:,} rows returned."
            )
            st.dataframe(
                query_result.to_pandas(),
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download Query Results",
                data=query_result.write_csv(),
                file_name="sql_query_results.csv",
                mime="text/csv",
            )

        except Exception as exc:
            st.error(f"SQL query failed: {exc}")


# ============================================================
# AI ASSISTANT — GROQ + FALLBACK
# ============================================================

elif page == "🤖 AI Assistant":
    show_page_header(
        "🤖 AI Analytics Assistant",
        "Ask questions about your data using your existing Groq-powered agent.",
    )
    require_dataset()

    user_question = st.text_input(
        "Ask a question about your dataset",
        placeholder="Example: Which columns have missing values?",
    )

    if st.button("✨ Ask Agent"):
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


# ============================================================
# MLFLOW TRACKING
# ============================================================

elif page == "📈 MLflow Tracking":
    show_page_header(
        "📈 MLflow Experiment Tracking",
        "Log dataset-quality metrics and save the generated report as an artifact.",
    )
    require_dataset()

    st.markdown("""
    Track dataset dimensions, missing values, duplicate rows,
    quality metrics, and the generated data-quality report.
    """)

    if st.button("🚀 Track Analysis with MLflow"):
        try:
            with st.spinner("Logging experiment to MLflow..."):
                run_id = track_dataset_analysis(df)

            st.success("Analysis tracked successfully!")
            st.markdown("**MLflow Run ID**")
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
                st.markdown("### 📋 Experiment History")
                st.dataframe(
                    runs_df,
                    use_container_width=True,
                    hide_index=True,
                )

                if "Quality Score" in runs_df.columns:
                    chart_df = runs_df.dropna(
                        subset=["Quality Score"]
                    )

                    if not chart_df.empty:
                        st.markdown("### 📊 Quality Score Comparison")

                        fig = px.bar(
                            chart_df,
                            x="Run ID",
                            y="Quality Score",
                            color="Quality Score",
                            color_continuous_scale="Viridis",
                            template="plotly_white",
                        )
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=35, b=10),
                        )
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                        )

            except Exception as exc:
                st.error(
                    f"Could not load MLflow runs: {exc}"
                )


    except Exception as exc:
        st.error(f"Could not generate report: {exc}")


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    AI Data Analytics Agent · Built with Python, Polars, DuckDB, Streamlit & MLflow
</div>
""", unsafe_allow_html=True)
