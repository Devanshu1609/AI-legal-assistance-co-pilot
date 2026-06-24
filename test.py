import os
import redis
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

try:
    redis_client.ping()
    print("Redis Connected Successfully")
except Exception as e:
    print("Redis Connection Failed:", e)