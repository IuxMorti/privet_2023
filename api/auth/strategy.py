from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from config import REDIS_HOST, REDIS_PORT, REDIS_PASS, SECRET

bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/login")


def get_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=60 * 60 * 24 * 30)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_strategy,
)
