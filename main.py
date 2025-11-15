import os
import uuid
import shutil
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import inspect
from pydantic import BaseModel

# Import your agents
from agents.document_processor_agent import DocumentProcessorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.question_answer_agent import QAAgent

# Config
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs/uploads")
VECTOR_DIR = "vector_store"

# Ensure directories exist at startup
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

class AskRequest(BaseModel):
    document_id: str
    question: str

# ---------- Helpers ----------
async def maybe_await(func_or_coro, *args, **kwargs):
    result = func_or_coro(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result

async def extract_content(agent_result):
    messages = agent_result.get("messages", [])
    if messages:
        msg_content = messages[-1].content
        try:
            return json.loads(msg_content)
        except Exception:
            return msg_content
    return None

# ---------- SSE Streaming Pipeline ----------
async def event_stream(file_path: str):
    """Generator to send live updates to frontend"""
    
    # Initialize agents
    processor_agent = await maybe_await(DocumentProcessorAgent().create_agent)
    summarizer_agent = await maybe_await(SummarizerAgent().create_agent)
    clause_agent = await maybe_await(ClauseExplainerAgent().create_agent)
    risk_agent = await maybe_await(RiskAnalysisAgent().create_agent)
    report_agent = await maybe_await(ReportGeneratorAgent().create_agent)

    # Document uploaded
    yield f"data: {{\"status\": \"uploaded\"}}\n\n"

    # Process document
    processed_doc_result = await processor_agent.ainvoke({"messages": [("user", file_path)]})
    extracted_text = await extract_content(processed_doc_result)
    yield f"data: {{\"status\": \"parsed\"}}\n\n"

    # Summarize & Clause Explanation concurrently
    summary_input = json.dumps({"extracted_text": extracted_text})
    clause_input = json.dumps({"summary": summary_input, "extracted_text": extracted_text})

    summary_task = summarizer_agent.ainvoke({"messages": [("user", summary_input)]})
    clause_task = clause_agent.ainvoke({"messages": [("user", clause_input)]})
    summary_result, clause_result = await asyncio.gather(summary_task, clause_task)

    summary_text = await extract_content(summary_result)
    clauses_text = await extract_content(clause_result)
    yield f"data: {{\"status\": \"summarized\"}}\n\n"
    yield f"data: {{\"status\": \"clauses_explained\"}}\n\n"

    # Risk Analysis
    risk_input_str = json.dumps({
        "summary": summary_text,
        "simplified_clauses": clauses_text,
        "extracted_text": extracted_text
    })
    risk_result = await risk_agent.ainvoke({"messages": [("user", risk_input_str)]})
    risk_text = await extract_content(risk_result)
    yield f"data: {{\"status\": \"risk_calculated\"}}\n\n"

    # Report Generation
    report_input_str = json.dumps({
        "file_name": os.path.basename(file_path),
        "vector_db_path": VECTOR_DIR,
        "extracted_text": extracted_text,
        "summary": summary_text,
        "clauses": clauses_text,
        "risk_assessment": risk_text
    })
    report_result = await report_agent.ainvoke({"messages": [("user", report_input_str)]})
    final_report_text = await extract_content(report_result)
    yield f"data: {{\"status\": \"completed\", \"report\": {json.dumps(final_report_text)}}}\n\n"

    # Save JSON output safely
    file_id = Path(file_path).stem.split("_")[0]
    output_file = OUTPUT_DIR / f"{file_id}_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_report_text, f, indent=2, ensure_ascii=False)
    except Exception as e:
        yield f"data: {{\"status\": \"error\", \"message\": \"Failed to save report: {str(e)}\"}}\n\n"

# ---------- Routes ----------
@app.post("/upload-stream")
async def upload_document_stream(file: UploadFile = File(...)):
    try:
        # Save file
       
        file_path = UPLOAD_DIR / f"{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Return streaming response
        return StreamingResponse(event_stream(str(file_path)), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: AskRequest):
    document_id = request.document_id
    question = request.question

    file_path = UPLOAD_DIR / document_id

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    qa_agent = QAAgent(doc_id=document_id, persist_directory=VECTOR_DIR)

    # FIX: remove await
    answer = qa_agent.answer(question)

    return {
        "document_id": document_id,
        "question": question,
        "answer": answer
    }



@app.get("/")
async def root():
    return {"status": "ok", "message": "🚀 Legal Document Assistant server is running"}

@app.get("/keep-alive")
async def keep_alive():
    return {"status": "active"}