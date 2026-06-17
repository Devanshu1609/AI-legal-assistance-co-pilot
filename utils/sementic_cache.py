import os
import json
import redis
import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_TTL = int(os.getenv("REDIS_TTL", 86400))
THRESHOLD = float(
    os.getenv("SEMANTIC_CACHE_THRESHOLD", 0.90)
)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

def save_semantic_cache(
        query,
        answer,
        source,
        file_name
):

    query_embedding = embeddings.embed_query(query)
    cache_data = {
        "query": query,
        "embedding": query_embedding,
        "answer": answer,
        "source": source,
        "file_name": file_name
    }

    cache_key = (f"semantic_cache:{file_name}:{hash(query)}")
    redis_client.setex(cache_key,REDIS_TTL,json.dumps(cache_data))
    redis_client.sadd(f"semantic_keys:{file_name}",cache_key)

def search_semantic_cache(query,file_name):

    query_embedding = np.array(embeddings.embed_query(query))
    cache_keys = redis_client.smembers(f"semantic_keys:{file_name}")
    best_similarity = -1
    best_answer = None

    for key in cache_keys:
        item = redis_client.get(key)
        if not item:
            continue
        data = json.loads(item)
        cached_embedding = np.array(data["embedding"])
        similarity = cosine_similarity([query_embedding],[cached_embedding])[0][0]
        if similarity > best_similarity:
            best_similarity = similarity
            best_answer = data

    if (
        best_answer and
        best_similarity >= THRESHOLD
    ):
        return {
            "hit": True,
            "answer": best_answer["answer"],
            "source": best_answer["source"],
            "similarity": float(best_similarity)
        }

    return {"hit": False}