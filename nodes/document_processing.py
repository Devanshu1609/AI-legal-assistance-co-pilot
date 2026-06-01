import fitz
import os
import re
import uuid
import hashlib

from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType
)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "legal_documents"


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=180,
    separators=["\n\n", "\n", ".", " ", ""]
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY,
    batch_size=64
)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def create_collection_if_not_exists():

    collections = qdrant.get_collections()

    existing_collections = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME in existing_collections:
        return

    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE
        )
    )

    # Required for filtering on file_name
    qdrant.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="file_name",
        field_schema=PayloadSchemaType.KEYWORD
    )

    # Optional but recommended
    qdrant.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="hash",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print(
        f"Collection '{COLLECTION_NAME}' created with indexes."
    )


def extract_pdf_content(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text("text")
        full_text += (f"\n\n--- Page {page_number + 1} ---\n")
        full_text += text

    return full_text

def generate_chunk_hash(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def load_existing_hashes():

    existing_hashes = set()
    offset = None
    while True:
        records, next_offset = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        if not records:
            break

        for point in records:

            chunk_hash = point.payload.get("hash")
            if chunk_hash:
                existing_hashes.add(chunk_hash)

        offset = next_offset
        if offset is None:
            break

    return existing_hashes


def process_document(file_path):

    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    create_collection_if_not_exists()

    file_name = os.path.basename(file_path)

    print("\n" + "=" * 60)
    print(f"Processing: {file_name}")
    print("=" * 60)

    text = extract_pdf_content(file_path)
    text = re.sub(r"\s+", " ", text)
    cleaned_text = text.strip()

    base_document = Document(
        page_content=cleaned_text,
        metadata={
            "file_name": file_name
        }
    )

    chunks = text_splitter.split_documents([base_document])
    print(f"Generated {len(chunks)} chunks")
    unique_hashes = set()
    unique_chunks = []

    for chunk in chunks:

        chunk_text = chunk.page_content.strip()
        chunk_hash = generate_chunk_hash(chunk_text)

        if chunk_hash in unique_hashes:
            continue

        unique_hashes.add(chunk_hash)

        chunk.metadata["hash"] = chunk_hash

        unique_chunks.append(chunk)

    print(f"After internal dedupe: "f"{len(unique_chunks)} chunks")
    print("Loading existing hashes from Qdrant...")
    existing_hashes = load_existing_hashes()
    print(f"Existing cached chunks: "f"{len(existing_hashes)}")

    new_chunks = []

    for chunk in unique_chunks:
        chunk_hash = chunk.metadata["hash"]
        if chunk_hash not in existing_hashes:
            new_chunks.append(chunk)

    print(f"New chunks to embed: "f"{len(new_chunks)}")

    if len(new_chunks) == 0:
        print("All chunks already exist.Skipping embeddings.")
        return {
            "file_name": file_name,
            "cleaned_text": cleaned_text,
            "total_chunks": len(chunks),
            "unique_chunks": len(unique_chunks),
            "new_chunks": 0,
            "stored_chunks": 0
        }

    print("Generating embeddings...")
    texts = [
        chunk.page_content
        for chunk in new_chunks
    ]

    vectors = embeddings.embed_documents(texts)
    print(f"Generated {len(vectors)} embeddings")

    points = []

    for chunk, vector in zip(new_chunks,vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "hash": chunk.metadata["hash"],
                    "file_name": file_name,
                    "text": chunk.page_content
                }
            )
        )

    print(f"Uploading {len(points)} vectors to Qdrant...")
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True
    )

    print(f"Successfully stored {len(points)} chunks.")

    return {
        "file_name": file_name,
        "total_chunks": len(chunks),
        "cleaned_text": cleaned_text,
        "unique_chunks": len(unique_chunks),
        "new_chunks": len(new_chunks),
        "stored_chunks": len(points)
    }

if __name__ == "__main__":

    result = process_document(
        r"D:\codebase\GEN-AI\AI-legal-assistance-co-pilot\Devanshu-GenAI-Resume (1)_merged.pdf"
    )

    print("\nSummary:")
    print(result)