import os
import uuid
import shutil
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import inspect

# Import your agents
from agents.document_processor_agent import DocumentProcessorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.question_answer_agent import QAAgent

# Config
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
VECTOR_DIR = "vector_store"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Legal Document Assistant")

# ---------- CORS ----------
origins = [
    "http://localhost:5173",
    "https://ai-legal-assistance-co-pilot-8rrj.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------
async def maybe_await(func_or_coro, *args, **kwargs):
    result = func_or_coro(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result

async def extract_content(agent_result):
    """Extract content from LangGraph agent output."""
    messages = agent_result.get("messages", [])
    if messages:
        msg_content = messages[-1].content
        try:
            return json.loads(msg_content)
        except Exception:
            return msg_content
    return None

# ---------- Pipeline ----------
async def run_pipeline(document_path: str):
    """Run multi-agent pipeline efficiently for a single document."""

    # Initialize agents
    processor_agent = await maybe_await(DocumentProcessorAgent().create_agent)
    summarizer_agent = await maybe_await(SummarizerAgent().create_agent)
    clause_agent = await maybe_await(ClauseExplainerAgent().create_agent)
    risk_agent = await maybe_await(RiskAnalysisAgent().create_agent)
    report_agent = await maybe_await(ReportGeneratorAgent().create_agent)

    # 1️⃣ Process document
    processed_doc_result = await processor_agent.ainvoke({"messages": [("user", document_path)]})
    extracted_text = await extract_content(processed_doc_result)

    # 2️⃣ Summarize & Clause Explanation concurrently
    summary_input = json.dumps({"extracted_text": extracted_text})
    clause_input = json.dumps({"summary": summary_input, "extracted_text": extracted_text})

    summary_task = summarizer_agent.ainvoke({"messages": [("user", summary_input)]})
    clause_task = clause_agent.ainvoke({"messages": [("user", clause_input)]})

    summary_result, clause_result = await asyncio.gather(summary_task, clause_task)

    summary_text = await extract_content(summary_result)
    clauses_text = await extract_content(clause_result)

    # 3️⃣ Risk Analysis
    risk_input_str = json.dumps({
        "summary": summary_text,
        "simplified_clauses": clauses_text,
        "extracted_text": extracted_text
    })
    risk_result = await risk_agent.ainvoke({"messages": [("user", risk_input_str)]})
    risk_text = await extract_content(risk_result)

    # 4️⃣ Report Generation
    report_input_str = json.dumps({
        "file_name": os.path.basename(document_path),
        "vector_db_path": VECTOR_DIR,
        "extracted_text": extracted_text,
        "summary": summary_text,
        "clauses": clauses_text,
        "risk_assessment": risk_text
    })
    report_result = await report_agent.ainvoke({"messages": [("user", report_input_str)]})
    final_report_text = await extract_content(report_result)

    return final_report_text

# ---------- Multi-document pipeline ----------
async def run_pipeline_multiple_docs(document_paths: list):
    """Process multiple documents concurrently."""
    async def process_single(doc_path):
        try:
            report = await run_pipeline(doc_path)
            return doc_path, report
        except Exception as e:
            return doc_path, {"error": str(e)}

    results = await asyncio.gather(*(process_single(p) for p in document_paths))
    return {doc_path: report for doc_path, report in results}

# ---------- Pydantic Model ----------
class AskRequest(BaseModel):
    document_id: str
    question: str

# ---------- Routes ----------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run pipeline
        final_report = await run_pipeline(str(file_path))

        # Save JSON output
        output_file = OUTPUT_DIR / f"{file_id}_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)

        return JSONResponse({
            "document_id": file_id,
            "file_name": file.filename,
            "report": final_report
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-multiple")
async def upload_multiple_documents(files: list[UploadFile] = File(...)):
    try:
        saved_paths = []
        file_ids = []

        for file in files:
            file_id = str(uuid.uuid4())
            file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_paths.append(str(file_path))
            file_ids.append(file_id)

        reports = await run_pipeline_multiple_docs(saved_paths)

        for file_id, file_path in zip(file_ids, saved_paths):
            output_file = OUTPUT_DIR / f"{file_id}_report.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(reports[file_path], f, indent=2, ensure_ascii=False)

        response = [
            {
                "document_id": fid,
                "file_name": Path(saved_paths[i]).name,
                "report": reports[saved_paths[i]]
            }
            for i, fid in enumerate(file_ids)
        ]
        return JSONResponse(response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: AskRequest):
    try:
        document_id = request.document_id
        question = request.question

        files = list(UPLOAD_DIR.glob(f"{document_id}_*"))
        if not files:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_path = str(files[0])

        qa_agent = QAAgent(doc_id=document_id, persist_directory=VECTOR_DIR)
        answer = await qa_agent.answer(question)  # ✅ directly await async

        return {"document_id": document_id, "question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "🚀 Legal Document Assistant server is running"}
