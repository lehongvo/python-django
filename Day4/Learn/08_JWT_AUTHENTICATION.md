## JWT Authentication with Django REST Framework (SimpleJWT)

This guide shows how to add JWT auth to a Django project using Django REST Framework (DRF) and SimpleJWT, including reading tokens from HttpOnly cookies for web flows and standard Authorization headers for API clients.

### 1) Install dependencies

```bash
pip install djangorestframework djangorestframework-simplejwt social-auth-app-django
```

### 2) Settings configuration

Add apps and DRF configuration, plus SimpleJWT options. Example:

```python
# settings.py
INSTALLED_APPS = [
    'rest_framework',
    'social_django',
    # ...
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'store.authentication.CookieJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### 3) Cookie-based JWT for web views

Create a small adapter so DRF can read the `access_token` from cookies when Authorization header is missing:

```python
# store/authentication.py
from typing import Optional, Tuple
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[object, str]]:
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
```

### 4) Issue and clear cookies in login/logout views

On successful login, set `access_token` (≈60m) and `refresh_token` (≈7d) as HttpOnly cookies. On logout, delete them.

```python
# store/views.py (excerpt)
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def user_login(request):
    if request.method == 'POST':
        # ... authenticate ...
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = redirect('store:account')
        secure_flag = not settings.DEBUG
        response.set_cookie('access_token', access_token, max_age=60*60, httponly=True, secure=secure_flag, samesite='Lax', path='/')
        response.set_cookie('refresh_token', refresh_token, max_age=7*24*60*60, httponly=True, secure=secure_flag, samesite='Lax', path='/')
        return response
    return render(request, 'store/login.html')

def logout_view(request):
    logout(request)
    response = redirect('store:home')
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/')
    return response
```

### 5) API endpoints

Expose JWT and profile endpoints via DRF:

```python
# store/urls_api.py (excerpt)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register_api, name='auth_register'),
    path('auth/me/', me_api, name='auth_me'),
]
```

Example `me` view using authentication decorators:

```python
# store/views_auth_api.py (excerpt)
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def me_api(request):
    return Response({'id': request.user.id, 'username': request.user.username, 'email': request.user.email})
```

### 6) How clients authenticate

- Web browser: Login form → server sets `access_token` cookie → DRF reads cookie via `CookieJWTAuthentication`.
- API clients (Postman, mobile): Send header `Authorization: Bearer <access>`.
- Refresh flow: POST `/api/auth/token/refresh/` with `{ "refresh": "..." }` to obtain a new access token; client should replace the old `access` or re-store cookie if your backend provides a cookie-based refresh endpoint.

### 7) Security notes

- Keep JWT cookies `HttpOnly`, `Secure` in production, and `SameSite=Lax` (or `Strict` if feasible).
- Rotate `SECRET_KEY` carefully; invalidates old tokens.
- Short access lifetime, longer refresh lifetime.
- CSRF: Header-based JWT APIs don’t need CSRF; cookie-based POSTs from browser should still respect CSRF for non-JSON form endpoints.

### 8) Quick test (cURL)

```bash
# Obtain tokens (if you use header-based login)
curl -X POST http://localhost:8001/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","password":"demo12345"}'

# Call protected endpoint with access token
curl http://localhost:8001/api/auth/me/ \
  -H 'Authorization: Bearer <ACCESS_TOKEN>'
```


