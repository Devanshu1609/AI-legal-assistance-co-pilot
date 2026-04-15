import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
import traceback
from graph.workflow import build_graph
from nodes.document_processing import process_document
from nodes.question_answer import hybrid_retrieve_and_rerank

app = FastAPI()

graph = build_graph()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

vectorstore = None
chunks = None
file_name = None
cleaned_text = None

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=500,
    timeout=None,
    max_retries=2,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    global vectorstore, chunks, file_name, cleaned_text

    try:
        print("STEP 1: File received")

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_name = file.filename
        file_path = os.path.join(UPLOAD_DIR, file_name)

        print("STEP 2: Saving file")

        with open(file_path, "wb") as f:
            f.write(await file.read())

        print("STEP 3: Processing document")

        vectorstore, cleaned_text, chunks = process_document(file_path)

        print("STEP 4: Running graph")

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

        print("STEP 5: Done")

        result.pop("messages", None)

        return {
            "message": "Document processed successfully",
            "report": result
        }

    except Exception as e:
        print("🔥 ERROR OCCURRED:")
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/ask-question")
async def ask_question(query: str):
    global chunks, file_name

    try:
        if chunks is None:
            raise HTTPException(
                status_code=400,
                detail="No document uploaded. Upload a document first."
            )

        context = hybrid_retrieve_and_rerank(query, file_name, chunks)
        messages = [
            (
                "system",
                "You are a helpful AI Legal Document Assistant. Use the provided context to answer the query accurately.",
            ),
            ("system", f"Context:\n{context}"),
            ("human", query),
        ]

        response = llm.invoke(messages)

        return {
            "query": query,
            "answer": response.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))