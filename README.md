# 📊 AI Data Analytics Agent

**An interactive data analytics platform built with Python, Streamlit, FastAPI, Polars, DuckDB, and Plotly.**

Upload a CSV dataset, explore its structure, identify data-quality issues, run SQL queries, ask natural-language questions, and generate downloadable analysis reports.

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

## ✨ Features

- **CSV Data Profiling** — Explore dataset dimensions, column names, data types, and descriptive statistics.
- **Data Quality Analysis** — Identify missing values and duplicate rows.
- **Interactive Visualizations** — Explore distributions and missing-value patterns using Plotly.
- **SQL Analytics** — Query uploaded datasets using DuckDB.
- **Analytics Agent** — Route natural-language questions to suitable analytics functions.
- **REST API** — Analyze uploaded CSV files using FastAPI endpoints.
- **Automated Reports** — Generate downloadable text reports with dataset summaries and data-quality findings.
- **Automated Testing** — Validate core functionality using pytest.
- **Docker Support** — Run the dashboard and API in a container.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Interactive dashboard |
| FastAPI | REST API |
| Polars | Data processing |
| DuckDB | SQL analytics |
| Plotly | Interactive charts |
| Pytest | Automated testing |
| Docker | Containerization |

## 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │       User           │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  Streamlit Dashboard │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  Analytics Agent     │
                 │  Question Routing    │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
        │ Polars   │  │ DuckDB   │  │ Plotly   │
        │ Profiling│  │ SQL      │  │ Charts   │
        └──────────┘  └──────────┘  └──────────┘

                 ┌──────────────────────┐
                 │   FastAPI REST API   │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │ Report Generation    │
                 └──────────────────────┘
```

## 📁 Project Structure

```text
ai-data-analytics-agent/
├── agent/
│   ├── graph.py
│   └── tools.py
├── analytics/
│   ├── profiling.py
│   ├── queries.py
│   └── charts.py
├── api/
│   └── main.py
├── app/
│   └── streamlit_app.py
├── evaluation/
├── reports/
│   └── report_generator.py
├── tests/
│   └── test_agent.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or compatible version
- Git
- Docker Desktop (optional)

### 1. Clone the repository

```bash
git clone https://github.com/Nagulanvelu/ai-data-analytics-agent.git
cd ai-data-analytics-agent
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the Streamlit dashboard

```bash
python -m streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

### 5. Start the FastAPI backend

Open a second terminal, activate the virtual environment, and run:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Useful endpoints:

- Dashboard: `http://localhost:8501`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## 🔎 API Usage

### Analyze a CSV dataset

Endpoint:

```http
POST /analyze
```

Example question:

```text
Which columns have missing values?
```

The API returns the filename, dataset dimensions, selected analytics tool, and results in JSON format.

### Generate an analysis report

Endpoint:

```http
POST /report
```

Upload a CSV file to generate a downloadable text report containing dataset information, duplicate counts, missing-value counts, and numeric summaries.

Use the interactive API documentation at `/docs` to test both endpoints.

## 🧪 Run Tests

```bash
python -m pytest tests/ -v
```

The initial test suite validates dataset overview, missing-value analysis, and report generation.

## 🐳 Run with Docker

Make sure Docker Desktop is running.

Build the image:

```bash
docker build -t ai-data-analytics-agent .
```

Run the container:

```bash
docker run --name analytics-agent -p 8000:8000 -p 8501:8501 ai-data-analytics-agent
```

Access the dashboard at `http://localhost:8501` and the API documentation at `http://localhost:8000/docs`.

## 💡 Example Use Cases

- Explore unfamiliar CSV datasets.
- Detect missing values and duplicate records.
- Generate descriptive statistics.
- Run SQL queries on uploaded data.
- Visualize numeric distributions.
- Export data-quality reports.
- Integrate analytics into other applications through a REST API.

## 🔭 Future Improvements

- Integrate an LLM for more flexible question answering.
- Add safer SQL validation and query resource limits.
- Introduce more advanced charts and automated insights.
- Add downloadable PDF and HTML reports.
- Implement GitHub Actions for continuous integration.
- Expand test coverage and API validation.

## 👨‍💻 Author

**Nagulanvelu**

B.Tech Artificial Intelligence Student | Python | Data Science | AI/ML

- GitHub: [@Nagulanvelu](https://github.com/Nagulanvelu)
- Project Repository: [AI Data Analytics Agent](https://github.com/Nagulanvelu/ai-data-analytics-agent)

---

*Built as a hands-on project to explore data analytics, API development, visualization, and deployment.*
