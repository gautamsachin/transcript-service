import redis
import os
import json

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

CACHE_TTL = int(os.getenv("CACHE_TTL", 86400))


def get_cache(video_id):

    key = f"yt_transcript:{video_id}"

    data = redis_client.get(key)

    if data:
        return json.loads(data)

    return None


def set_cache(video_id, value):

    key = f"yt_transcript:{video_id}"

    redis_client.setex(
        key,
        CACHE_TTL,
        json.dumps(value)
    )