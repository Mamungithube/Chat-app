from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self.inner)

class JWTAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        try:
            query_string = self.scope.get('query_string', b'').decode()
            print("Raw query string:", query_string)  # Debug
            query_params = parse_qs(query_string)
            print("Parsed query params:", query_params)  # Debug
            token = query_params.get("token", [None])[0]
            
            if token:
                print("Token found:", token)  # Debug
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                print("User ID from token:", user_id)  # Debug
                user = await get_user(user_id)
                print("User object:", user)  # Debug
                self.scope["user"] = user
            else:
                print("No token provided")  # Debug
                self.scope["user"] = AnonymousUser()
        except Exception as e:
            print("JWT Middleware Error:", e)
            self.scope["user"] = AnonymousUser()

        return await self.inner(self.scope, receive, send)