import os
import uuid
import shutil
import json
import asyncio
import inspect
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

# Import your agents / graph
from agents.document_processor_agent import DocumentProcessorAgent
from agents.summarizer_agent import SummarizerAgent
from agents.clause_explainer_agent import ClauseExplainerAgent
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.supervisor_agent import SupervisorAgent
from agents.question_answer_agent import QAAgent
from graph.multi_agent_graph import MultiAgentGraph

# Config
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
VECTOR_DIR = "vector_store"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Legal Document Assistant")

# ---------- Helpers ----------
async def maybe_await(func_or_coro, *args, **kwargs):
    """Call either a regular function or coroutine function and return result."""
    result = func_or_coro(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


async def run_pipeline(document_path: str):
    """Run multi-agent pipeline on the uploaded document and return final report dict."""

    # 1. Initialize agents
    agent_classes = {
        "document_processor_agent": DocumentProcessorAgent,
        "summarizer_agent": SummarizerAgent,
        "clause_explainer_agent": ClauseExplainerAgent,
        "risk_analysis_agent": RiskAnalysisAgent,
        "report_generator_agent": ReportGeneratorAgent,
        "supervisor": SupervisorAgent,
    }

    agents = {}
    for key, cls in agent_classes.items():
        instance = cls()
        agents[key] = await maybe_await(instance.create_agent)

    # 2. Build graph
    graph_builder = MultiAgentGraph(agents)
    graph_builder.build_graph()
    app_graph = graph_builder.compile()

    # 3. Run
    result = await app_graph.ainvoke({"messages": [("user", document_path)]})

    # 4. Extract report
    final_report = None
    for msg in result.get("messages", []):
        if hasattr(msg, "name") and msg.name == "report_generator_agent":
            try:
                final_report = json.loads(msg.content)
            except Exception:
                final_report = {"raw_output": msg.content}
            break

    if not final_report:
        raise ValueError("Report could not be generated.")

    return final_report


# ---------- Routes ----------
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document, run pipeline, and return summary/report."""
    try:
        # Save uploaded file
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

        return JSONResponse(
            {
                "document_id": file_id,
                "file_name": file.filename,
                "report": final_report,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_question(document_id: str = Form(...), question: str = Form(...)):
    """Ask a question about a previously uploaded document."""
    try:
        # Find uploaded document by ID
        files = list(UPLOAD_DIR.glob(f"{document_id}_*"))
        if not files:
            raise HTTPException(status_code=404, detail="Document not found")

        doc_path = str(files[0])

        # Init QAAgent
        qa_agent = QAAgent(doc_id=doc_path, persist_directory=VECTOR_DIR)

        # Answer (sync/async support)
        answer_fn = getattr(qa_agent, "answer", None)
        if not answer_fn:
            raise HTTPException(status_code=500, detail="QA agent has no answer method")

        if inspect.iscoroutinefunction(answer_fn):
            answer = await answer_fn(question)
        else:
            answer = await asyncio.to_thread(answer_fn, question)

        return {"document_id": document_id, "question": question, "answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "🚀 Legal Document Assistant server is running"}
