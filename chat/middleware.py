from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token['user_id']
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()

class JWTAuthMiddleware:
    """
    Custom middleware that authenticates WebSocket connection via JWT token in query string.
    ASGI 3 compatible middleware.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Parse token from query string
        query_string = parse_qs(scope["query_string"].decode())
        token_key = query_string.get("token", [None])[0]

        scope["user"] = await get_user(token_key)

        return await self.app(scope, receive, send)
