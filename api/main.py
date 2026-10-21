
from io import BytesIO

import polars as pl
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from agent.graph import answer_question_with_groq
from fastapi.responses import PlainTextResponse
from reports.report_generator import generate_report

app = FastAPI(
    title="AI Data Analytics Agent API",
    description="Upload CSV files and ask questions about your data.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "AI Data Analytics Agent API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    question: str = Query(
        default="Give me a dataset overview",
        min_length=1,
        max_length=500,
    ),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        df = pl.read_csv(
            BytesIO(content),
            infer_schema_length=10000,
        )

        response = answer_question_with_groq(df, question)
        result = response["result"]

        if isinstance(result, pl.DataFrame):
            result = result.to_dicts()

        return {
            "filename": file.filename,
            "rows": df.height,
            "columns": df.width,
            "question": question,
            "selected_tool": response["tool"],
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {exc}",
        ) from exc
    finally:
        await file.close()


@app.post("/report", response_class=PlainTextResponse)
async def download_report(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    try:
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        df = pl.read_csv(BytesIO(content), infer_schema_length=10000)
        report = generate_report(df)

        return PlainTextResponse(
            content=report,
            headers={
                "Content-Disposition":
                    'attachment; filename="analytics_report.txt"'
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Report generation failed: {exc}",
        ) from exc
    finally:
        await file.close()
