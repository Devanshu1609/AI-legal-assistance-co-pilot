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
from utils.sementic_cache import (
    save_semantic_cache,
    search_semantic_cache
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
        print("Received file:", file_name)
        file_path = os.path.join(UPLOAD_DIR, file_name)
        print("Saving file to:", file_path)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        document_result = process_document(file_path)
        cleaned_text = document_result["cleaned_text"]

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
        print("file_name", file_name)
        file_path = os.path.join(UPLOAD_DIR, file_name)
        print("file_path", file_path)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        semantic_cache_result = search_semantic_cache(query, file_name)
        if semantic_cache_result["hit"]:
            print("Semantic cache hit with similarity:", semantic_cache_result["similarity"])
            return {
                "query": query,
                "answer": semantic_cache_result["answer"],
                "source": semantic_cache_result["source"],
                "file_name": file_name,
                "similarity": semantic_cache_result["similarity"]
            }

        local_context = hybrid_retrieve_and_rerank(query, file_name)
        can_answer_locally = check_local_knowledge(query, local_context)

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
                Answer ONLY from the provided context.

                Rules:
                - Only answer from the provided context.
                - properly explain your answers.
                - Do not add assumptions.
                """
            ),
            (
                "system",
                f"Context:\n{final_context}"
            ),
            ("human", query),
        ]

        response = llm.invoke(messages)

        save_semantic_cache(
            query=query,
            answer=response.content,
            source=source,
            file_name=file_name
        )

        return {
            "query": query,
            "answer": response.content,
            "source": source,
            "file_name": file_name
        }

    except Exception as e:
        print("ERROR IN /ask-question")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Server is running"}