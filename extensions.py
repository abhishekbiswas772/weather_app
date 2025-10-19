from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://"
)

# Synchronous Redis connection pool (thread-safe)
_redis_pool = None

def get_redis_client():
    """Get a synchronous Redis client from the connection pool"""
    global _redis_pool
    if _redis_pool is None:
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("Redis url not found....")
        _redis_pool = redis.ConnectionPool.from_url(redis_url, decode_responses=True, max_connections=10)
    return redis.Redis(connection_pool=_redis_pool)