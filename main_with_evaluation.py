"""FastAPI server with integrated evaluation metrics."""

import os
import time
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq

from graph.workflow import build_graph
from nodes.document_processing import process_document
from nodes.question_answer import hybrid_retrieve_and_rerank
from utils.decision_layer import (
    check_local_knowledge,
    get_web_context
)
from evaluation.evaluator import LegalAssistantEvaluator
from evaluation.metrics import LatencyTracker

# ============================================================================
# SETUP
# ============================================================================

app = FastAPI(title="Legal Assistant with Evaluation")
graph = build_graph()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=500,
)

# INITIALIZE EVALUATION TOOLS
evaluator = LegalAssistantEvaluator(output_dir="evaluations")
latency_tracker = LatencyTracker(log_dir="logs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QuestionRequest(BaseModel):
    query: str
    file_name: str

# ============================================================================
# INSTRUMENTED ENDPOINTS
# ============================================================================

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process document with LATENCY MEASUREMENT
    """
    document_start = time.time()
    
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files allowed"
            )

        file_name = file.filename
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # TIME: File save
        file_save_start = time.time()
        with open(file_path, "wb") as f:
            f.write(await file.read())
        file_save_time = time.time() - file_save_start

        # TIME: Document processing
        doc_process_start = time.time()
        vectorstore, cleaned_text, chunks = process_document(file_path)
        doc_process_time = time.time() - doc_process_start

        # TIME: Graph invocation
        graph_start = time.time()
        result = await graph.ainvoke(
            {
                "extracted_text": cleaned_text,
                "summary": None,
                "clause_explanation": None,
                "risk_analysis": None,
                "report": None,
                "messages": []
            },
            config={"recursion_limit": 100}
        )
        graph_time = time.time() - graph_start

        result.pop("messages", None)

        # Total timing
        total_time = time.time() - document_start

        # LOG METRICS
        evaluation_result = evaluator.evaluate_document_processing(
            file_path=file_path,
            processing_time=total_time,
            extracted_text=cleaned_text,
            expected_content=cleaned_text[:500]
        )

        return {
            "message": "Document processed successfully",
            "file_name": file_name,
            "report": result,
            "metrics": {
                "file_save_ms": float(file_save_time * 1000),
                "document_processing_ms": float(doc_process_time * 1000),
                "graph_execution_ms": float(graph_time * 1000),
                "total_latency_ms": float(total_time * 1000),
                "text_length": len(cleaned_text),
                "chunk_count": len(chunks),
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/ask-question")
async def ask_question(data: QuestionRequest):
    """
    Q&A with RAG pipeline + FULL EVALUATION
    Measures: retrieval latency, generation latency, RAG quality
    """
    qa_start = time.time()
    
    try:
        query = data.query
        file_name = data.file_name

        file_path = os.path.join(UPLOAD_DIR, file_name)

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        # STEP 1: Re-process document
        vectorstore, cleaned_text, chunks = process_document(file_path)

        # STEP 2: HYBRID RETRIEVAL (measure latency)
        retrieval_start = time.time()
        local_context_docs = hybrid_retrieve_and_rerank(
            query,
            file_name,
            chunks
        )
        retrieval_time = time.time() - retrieval_start
        
        # Convert docs to string
        local_context = "\n".join([
            doc.page_content for doc in local_context_docs
        ])

        # STEP 3: Decision layer
        can_answer_locally = check_local_knowledge(
            query,
            local_context
        )

        if can_answer_locally:
            final_context = local_context
            source = "document"
        else:
            final_context = get_web_context(query)
            source = "web"

        # STEP 4: GENERATION (measure latency)
        generation_start = time.time()
        messages = [
            (
                "system",
                """
                You are an AI legal assistant.
                Use the provided context to answer accurately.
                Do not hallucinate or add information not in context.
                """
            ),
            (
                "system",
                f"Context:\n{final_context}"
            ),
            ("human", query),
        ]

        response = llm.invoke(messages)
        generation_time = time.time() - generation_start

        total_qa_time = time.time() - qa_start

        # STEP 5: EVALUATE RAG PIPELINE
        rag_eval = evaluator.evaluate_qa_pipeline(
            query=query,
            retrieved_chunks=[doc.page_content for doc in local_context_docs],
            answer=response.content,
            ground_truth_answer="",
            latency=total_qa_time,
            retrieval_latency=retrieval_time
        )

        return {
            "query": query,
            "answer": response.content,
            "source": source,
            "file_name": file_name,
            "metrics": {
                "retrieval_latency_ms": float(retrieval_time * 1000),
                "generation_latency_ms": float(generation_time * 1000),
                "total_latency_ms": float(total_qa_time * 1000),
                "retrieved_chunk_count": len(local_context_docs),
                "context_length": len(final_context),
                "rag_evaluation": rag_eval
            }
        }

    except Exception as e:
        print("ERROR IN /ask-question")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/metrics")
def get_metrics():
    """Get aggregated evaluation metrics"""
    return {
        "latency_stats": latency_tracker.get_by_operation(),
        "timestamp": time.time()
    }

@app.get("/")
def home():
    return {"message": "Server is running with evaluation", "docs": "/docs"}
