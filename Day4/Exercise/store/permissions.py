from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.conf import settings


class ApiKeyPermission(BasePermission):
    """Require a valid API key for all DRF endpoints.

    - Accepts either header: "Authorization: Api-Key <key>" or "X-API-Key: <key>".
    - Compares against settings.GLOBAL_API_KEY (string) or a list in settings.GLOBAL_API_KEYS.
    """

    def has_permission(self, request, view):
        # Allow safe (read-only) requests without an API key for public browsing
        if request.method in SAFE_METHODS:
            return True
        # If the user is already authenticated (Session/JWT), allow without API key.
        # This keeps the website UX working while still protecting external access.
        user = getattr(request, 'user', None)
        if getattr(user, 'is_authenticated', False):
            return True

        # Extract from headers
        auth_header = request.headers.get('Authorization', '')
        provided = None
        if auth_header.startswith('Api-Key '):
            provided = auth_header.split(' ', 1)[1].strip()
        if not provided:
            provided = request.headers.get('X-API-Key')

        if not provided:
            return False

        # Support single or multiple keys via settings
        valid_keys = []
        if getattr(settings, 'GLOBAL_API_KEY', None):
            valid_keys.append(settings.GLOBAL_API_KEY)
        if getattr(settings, 'GLOBAL_API_KEYS', None):
            valid_keys.extend(settings.GLOBAL_API_KEYS)

        return provided in valid_keys


