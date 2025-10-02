import os
import logging
from PIL import Image
import pytesseract
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.tools import Tool

load_dotenv()

# ---------------------- Logging Setup ---------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class DocumentProcessorTools:
    def __init__(self, persist_directory="vector_store", chunk_size=1000, chunk_overlap=200, batch_size=100):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "."]
        )
        self.batch_size = batch_size

    # ------------------- Load Document Parallel ------------------- #
    def load_document_parallel(self, file_path):
        ext = file_path.split('.')[-1].lower()

        if ext == "pdf":
            loader = PyPDFLoader(file_path)
            return loader.load_and_split()

        elif ext == "docx":
            loader = Docx2txtLoader(file_path)
            return loader.load()

        elif ext in ["png", "jpg", "jpeg"]:
            text = pytesseract.image_to_string(Image.open(file_path), config="--psm 3")
            return [Document(page_content=text)]

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    # ------------------- Extract Text ------------------- #
    def extract_text(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        documents = self.load_document_parallel(file_path)
        return " ".join(doc.page_content for doc in documents)

    # ------------------- Chunk Documents Parallel ------------------- #
    def chunk_documents_parallel(self, documents):
        if len(documents) <= 1:
            return self.splitter.split_documents(documents)
        with ThreadPoolExecutor() as executor:
            chunk_lists = list(executor.map(lambda doc: self.splitter.split_documents([doc]), documents))
        return [chunk for sublist in chunk_lists for chunk in sublist]

    # ------------------- Vector DB Handling ------------------- #
    def get_vectordb(self):
        try:
            if os.path.exists(self.persist_directory):
                vectordb = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                vectordb = Chroma.from_documents(
                    documents=[],
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
            return vectordb
        except Exception as e:
            logging.warning(f"Vector DB initialization failed: {e}. Creating new DB.")
            return Chroma.from_documents(
                documents=[],
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

    def store_in_vectordb_batch(self, chunks):
        vectordb = self.get_vectordb()
        for i in range(0, len(chunks), self.batch_size):
            vectordb.add_documents(chunks[i:i+self.batch_size])
        vectordb.persist()
        return vectordb

    # ------------------- Full Document Processing ------------------- #
    def process_document(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        logging.info(f"Processing document: {file_path}")
        try:
            documents = self.load_document_parallel(file_path)
            if not documents:
                return {"error": "No text extracted from document."}

            chunks = self.chunk_documents_parallel(documents)
            self.store_in_vectordb_batch(chunks)
            extracted_text = " ".join(doc.page_content for doc in documents)

            return {
                "file_name": os.path.basename(file_path),
                "num_chunks": len(chunks),
                "vector_db_path": self.persist_directory,
                "extracted_text": extracted_text
            }

        except Exception as e:
            logging.error(f"Error processing document: {e}")
            return {"error": str(e)}

    # ------------------- Store Metadata ------------------- #
    def store_metadata(self, content: str, meta_type: str, source_file: str):
        if not content.strip():
            return {"error": "Empty content, nothing to store."}

        document = Document(
            page_content=content,
            metadata={"type": meta_type, "source": source_file}
        )
        vectordb = self.store_in_vectordb_batch([document])
        return {
            "status": "success",
            "stored_type": meta_type,
            "source_file": source_file,
            "vector_db_path": self.persist_directory
        }

    # ------------------- LangGraph Tools ------------------- #
    def get_tools(self):
        return [
            Tool(
                name="process_document",
                func=self.process_document,
                description=(
                    "Process and store a document (PDF, DOCX, PNG, JPG, JPEG) into the vector database. "
                    "Returns JSON with file name, chunk count, DB path, and extracted text."
                )
            ),
            Tool(
                name="extract_text",
                func=self.extract_text,
                description=(
                    "Extract raw text from a document without storing it in the DB. "
                    "Useful for passing plain text to other agents."
                )
            ),
            Tool(
                name="store_metadata",
                func=lambda args: self.store_metadata(
                    args["content"], args["type"], args.get("source", "unknown")
                ),
                description=(
                    "Store AI-generated metadata (summary, risks, clauses, etc.) in the vector DB. "
                    "Input must be a dict with {content: str, type: str, source: str}."
                )
            )
        ]
