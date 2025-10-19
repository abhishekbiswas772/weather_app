from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis.asyncio as redis
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://"
)

async def get_redis_client():
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise ValueError("Redis url not found....")
    return redis.from_url(redis_url, decode_responses=True)