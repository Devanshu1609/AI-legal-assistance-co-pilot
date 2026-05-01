import os
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

app = FastAPI()
graph = build_graph()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=500,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    query: str
    file_name: str


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files allowed"
            )

        file_name = file.filename
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        vectorstore, cleaned_text, chunks = process_document(file_path)

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

        result.pop("messages", None)

        return {
            "message": "Document processed successfully",
            "file_name": file_name,
            "report": result
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/ask-question")
async def ask_question(data: QuestionRequest):
    try:
        query = data.query
        file_name = data.file_name

        file_path = os.path.join(
            UPLOAD_DIR,
            file_name
        )

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        vectorstore, cleaned_text, chunks = process_document(file_path)

        local_context = hybrid_retrieve_and_rerank(
            query,
            file_name,
            chunks
        )

        can_answer_locally = check_local_knowledge(
            query,
            local_context
        )

        print(
            f"Can answer locally: {can_answer_locally}"
        )

        if can_answer_locally:
            final_context = local_context
            source = "document"
        else:
            final_context = get_web_context(query)
            source = "web"

        messages = [
            (
                "system",
                """
                You are an AI legal assistant.
                Use the provided context to answer accurately.
                """
            ),
            (
                "system",
                f"Context:\n{final_context}"
            ),
            ("human", query),
        ]

        response = llm.invoke(messages)

        return {
            "query": query,
            "answer": response.content,
            "source": source,
            "file_name": file_name
        }

    except Exception as e:
        print("ERROR IN /ask-question")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )