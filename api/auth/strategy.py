from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

import redis.asyncio

import config

bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/login")


redis = redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
