# question_answer.py

import os
import numpy as np
import cohere
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import (
    cosine_similarity
)
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)
from langchain_core.documents import Document
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "legal_documents"
co = cohere.ClientV2(COHERE_API_KEY)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY,
    batch_size=100
)

qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def load_chunks_from_qdrant(file_name):
    chunks = []
    offset = None
    while True:
        points, next_offset = qdrant.scroll(
            collection_name=COLLECTION_NAME,

            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="file_name",
                        match=MatchValue(value=file_name)
                    )
                ]
            ),
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        if not points:
            break

        for point in points:

            chunks.append(
                Document(
                    page_content=point.payload["text"],
                    metadata={"file_name": file_name}
                )
            )

        offset = next_offset
        if offset is None:
            break

    return chunks

def maximal_marginal_relevance(
    query_embedding,
    doc_embeddings,
    docs,
    k=5,
    lambda_mult=0.5
):

    if len(docs) <= k:
        return docs
    
    selected_indices = []
    similarities_to_query = cosine_similarity([query_embedding],doc_embeddings)[0]

    first_idx = np.argmax(similarities_to_query)
    selected_indices.append(first_idx)

    while len(selected_indices) < k:

        best_score = -float("inf")
        best_idx = None

        for idx in range(len(docs)):
            if idx in selected_indices:
                continue
            relevance = (similarities_to_query[idx])

            diversity = max(
                cosine_similarity([doc_embeddings[idx]], [doc_embeddings[j]])[0][0]
                for j in selected_indices
            )

            mmr_score = (lambda_mult * relevance - (1 - lambda_mult)* diversity)
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        selected_indices.append(best_idx)

    return [
        docs[idx]
        for idx in selected_indices
    ]

def dense_mmr_retrieve(
    query,
    file_name,
    k=5,
    fetch_k=20
):

    query_embedding = (embeddings.embed_query(query))

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=fetch_k,
        with_payload=True,
        with_vectors=True,
        query_filter=Filter(
            must=[
                FieldCondition(key="file_name", match=MatchValue(value=file_name))
            ]
        )
    )

    docs = []
    doc_embeddings = []
    for point in results.points:
        docs.append(
            Document(
                page_content=point.payload["text"],
                metadata={
                    "file_name":point.payload.get("file_name"),
                    "score":point.score
                }
            )
        )
        doc_embeddings.append(point.vector)

    if not docs:
        return []

    doc_embeddings = np.array(doc_embeddings)

    mmr_docs = (
        maximal_marginal_relevance(
            query_embedding=query_embedding,
            doc_embeddings=doc_embeddings,
            docs=docs,
            k=k,
            lambda_mult=0.5
        )
    )
    return mmr_docs

def sparse_retrieve(
    documents,
    query,
    k=10
):

    corpus = [doc.page_content for doc in documents]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = (query.lower().split())
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [
        documents[i]
        for i in top_indices
    ]

def reciprocal_rank_fusion(
    dense_docs,
    sparse_docs,
    k=60
):

    fused_scores = {}

    for rank, doc in enumerate(dense_docs):
        key = doc.page_content
        fused_scores[key] = (fused_scores.get(key, 0) + 1 / (k + rank + 1))

    for rank, doc in enumerate(sparse_docs):
        key = doc.page_content
        fused_scores[key] = (
            fused_scores.get(key, 0) + 1 / (k + rank + 1))

    sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

    content_to_doc = {
        doc.page_content: doc
        for doc in (dense_docs + sparse_docs)
    }

    return [
        content_to_doc[item[0]]
        for item in sorted_docs
    ]

def cohere_rerank(
    query,
    docs,
    top_k=5
):

    if not docs:
        return []

    texts = [
        doc.page_content
        for doc in docs
]

    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=texts,
        top_n=min(top_k, len(texts))
    )

    reranked_docs = [
        docs[result.index]
        for result in response.results
    ]
    return reranked_docs


def hybrid_retrieve_and_rerank(query, file_name):
    dense_docs = (
        dense_mmr_retrieve(
            query=query,
            file_name=file_name,
            k=5,
            fetch_k=20
        )
    )

    chunks = load_chunks_from_qdrant(file_name)
    sparse_docs = sparse_retrieve(chunks, query, k=10)
    fused_docs = (reciprocal_rank_fusion(dense_docs, sparse_docs))
    final_docs = (cohere_rerank(query, fused_docs, top_k=5))
    return final_docs