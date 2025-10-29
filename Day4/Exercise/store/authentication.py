from typing import Optional, Tuple
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Allow JWT auth via 'access_token' cookie when Authorization header is missing."""

    def authenticate(self, request: Request) -> Optional[Tuple[object, str]]:
        # Try standard Authorization header first
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        # Fallback to cookie-based token
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


