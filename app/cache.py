import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

CACHE_TTL = 86400


def get_cache(video_id):
    data = redis_client.get(video_id)

    if data:
        return json.loads(data)

    return None


def set_cache(video_id, value):
    redis_client.setex(
        video_id,
        CACHE_TTL,
        json.dumps(value)
    )