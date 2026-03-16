# question_answer.py

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    batch_size=32,
    google_api_key=GOOGLE_API_KEY
)


def dense_mmr_retrieve(vectorstore, query, k=5, fetch_k=20):
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k}
    )
    print(f"Performing dense MMR retrieval with k={k} and fetch_k={fetch_k}...")
    return retriever.invoke(query)


def sparse_retrieve(documents, query, k=10):
    corpus = [doc.page_content for doc in documents]
    tokenized_corpus = [doc.lower().split() for doc in corpus]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    print(f"Performing sparse BM25 retrieval with k={k}...")

    return [documents[i] for i in top_indices]

def reciprocal_rank_fusion(dense_docs, sparse_docs, k=60):
    fused_scores = {}

    for rank, doc in enumerate(dense_docs):
        key = doc.page_content
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (k + rank + 1)

    for rank, doc in enumerate(sparse_docs):
        key = doc.page_content
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (k + rank + 1)

    sorted_docs = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    content_to_doc = {
        doc.page_content: doc for doc in dense_docs + sparse_docs
    }

    print(f"Performing Reciprocal Rank Fusion on {len(dense_docs)} dense and {len(sparse_docs)} sparse docs...")

    return [content_to_doc[item[0]] for item in sorted_docs]


reranker = CrossEncoder("BAAI/bge-reranker-base")


def cross_encoder_rerank(query, docs, top_k=5):
    pairs = [(query, doc.page_content) for doc in docs]
    scores = reranker.predict(pairs)

    scored_docs = list(zip(docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    print(f"Performing Cross-Encoder re-ranking on {len(docs)} documents...")

    return [doc for doc, score in scored_docs[:top_k]]


def hybrid_retrieve_and_rerank(query, file_name , chunks):
    persist_directory = f"./chroma_legal_db/{file_name}"

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    dense_docs = dense_mmr_retrieve(vectorstore, query)
    sparse_docs = sparse_retrieve(chunks, query)
    fused_docs = reciprocal_rank_fusion(dense_docs, sparse_docs)
    final_docs = cross_encoder_rerank(query, fused_docs)

    return final_docs