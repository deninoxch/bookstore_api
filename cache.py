import redis

# Кэшируем ТОЛЬКО полный список книг (GET /books без параметров)
CACHE_KEY = "books:all"
CACHE_TTL = 60  # секунды, по условию задания

# decode_responses=True: redis-py вернёт str, а не bytes
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def cache_get(key: str):
    return r.get(key)


def cache_setex(key: str, ttl: int, value: str):
    r.setex(key, ttl, value)


def cache_delete(key: str):
    r.delete(key)
