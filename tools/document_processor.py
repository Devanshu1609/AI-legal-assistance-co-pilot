import os
from PIL import Image
import pytesseract
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.tools import Tool
import json

load_dotenv()

class DocumentProcessorTools:
    def __init__(self, persist_directory="vector_store"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def load_document(self, file_path):
        """Load PDF, DOCX, or image and return a list of Document objects."""
        ext = file_path.split('.')[-1].lower()

        if ext == "pdf":
            loader = PyPDFLoader(file_path)
            return loader.load()

        elif ext == "docx":
            loader = Docx2txtLoader(file_path)
            return loader.load()

        elif ext in ["png", "jpg", "jpeg"]:
            text = pytesseract.image_to_string(Image.open(file_path))
            return [Document(page_content=text)]

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def extract_text(self, file_path):
        """Extract raw text from a document without storing in DB."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        documents = self.load_document(file_path)
        extracted_text = " ".join([doc.page_content for doc in documents])
        return extracted_text

    def chunk_document(self, documents):
        """Split documents into smaller chunks for embeddings."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        return text_splitter.split_documents(documents)

    def get_vectordb(self):
        """Load or initialize Chroma vector database."""
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

    def store_in_vectordb(self, chunks):
        """Store document chunks in ChromaDB persistently."""
        vectordb = self.get_vectordb()
        vectordb.add_documents(chunks)
        vectordb.persist()
        return vectordb

    def process_document(self, file_path: str) -> dict:
        """
        Ingest a document into ChromaDB for retrieval-based QA.
        Returns structured JSON with details.
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        print(f"\nEXECUTING TOOL: Ingesting document '{file_path}'...")

        documents = self.load_document(file_path)
        chunks = self.chunk_document(documents)
        self.store_in_vectordb(chunks)
        extracted_text = " ".join([doc.page_content for doc in documents])

        result = {
            "file_name": os.path.basename(file_path),
            "num_chunks": len(chunks),
            "vector_db_path": self.persist_directory,
            "extracted_text": extracted_text
        }
        return result

    def store_metadata(self, content: str, meta_type: str, source_file: str):
        """
        Store AI-generated metadata (summary, risks, clauses, etc.)
        as a document in the vector DB.
        """
        if not content.strip():
            return {"error": "Empty content, nothing to store."}

        document = Document(
            page_content=content,
            metadata={"type": meta_type, "source": source_file}
        )
        vectordb = self.store_in_vectordb([document])

        return {
            "status": "success",
            "stored_type": meta_type,
            "source_file": source_file,
            "vector_db_path": self.persist_directory
        }

    def get_tools(self):
        """Return a list of tools for LangChain agents."""
        return [
            Tool(
                name="process_document",
                func=self.process_document,
                description=(
                    "Use this tool to process and store the content of a document "
                    "(PDF, DOCX, PNG, JPG, JPEG) into the vector database for later retrieval. "
                    "Returns structured JSON with file name, chunk count, DB path, and extracted text."
                )
            ),
            Tool(
                name="extract_text",
                func=self.extract_text,
                description=(
                    "Use this tool to extract raw text from a document without storing it in the DB. "
                    "Useful for passing plain text to other agents."
                )
            ),
            Tool(
                name="store_metadata",
                func=lambda args: self.store_metadata(args["content"], args["type"], args.get("source", "unknown")),
                description=(
                    "Use this tool to store AI-generated metadata (like summary, risk analysis, or clauses) "
                    "in the vector DB. Input must be a dict with {content: str, type: str, source: str}."
                )
            )
        ]
