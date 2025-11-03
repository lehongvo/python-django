from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import ApiKeyPermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .serializers import CustomerSerializer
from .models import Customer
from .utils import assign_welcome_promo_and_email, claim_unused_promos
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string',
                    'description': 'Username for the new account',
                    'example': 'johndoe'
                },
                'password': {
                    'type': 'string',
                    'format': 'password',
                    'description': 'Password for the new account',
                    'example': 'SecurePass123!'
                },
                'email': {
                    'type': 'string',
                    'format': 'email',
                    'description': 'Email address (optional)',
                    'example': 'john@example.com'
                }
            },
            'required': ['username', 'password']
        }
    },
    responses={
        201: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'example': 'Registered successfully'},
                'user': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'username': {'type': 'string', 'example': 'johndoe'},
                        'email': {'type': 'string', 'example': 'john@example.com'}
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'example': 'username and password are required'}
            }
        }
    },
    examples=[
        OpenApiExample(
            'Register User',
            value={
                'username': 'johndoe',
                'password': 'SecurePass123!',
                'email': 'john@example.com'
            },
            request_only=True
        ),
    ]
)
@api_view(['POST'])
@permission_classes([ApiKeyPermission, AllowAny])
@throttle_classes([ScopedRateThrottle])
def register_api(request):
    """Register a new user and return minimal profile info."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    email = request.data.get('email', '').strip()

    if not username or not password:
        return Response({'error': 'username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as ve:
        return Response({'error': ve.messages}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email or None, password=password)

    # Create or link customer record
    customer_email = user.email or f"{user.username}@example.com"
    customer, _ = Customer.objects.get_or_create(
        email=customer_email,
        defaults={
            'name': user.get_full_name() or user.username,
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': 'USA',
        },
    )
    if customer.user_id in (None, user.id):
        customer.user = user
        customer.save(update_fields=['user'])

    # Assign welcome promos (8) and send email
    try:
        assign_welcome_promo_and_email(user, count=8)
    except Exception:
        pass

    return Response({
        'message': 'Registered successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_201_CREATED)

# Set ScopedRateThrottle scope for function-based view
register_api.throttle_scope = 'auth'


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'id': {'type': 'integer', 'example': 1},
                'username': {'type': 'string', 'example': 'johndoe'},
                'email': {'type': 'string', 'example': 'john@example.com'},
                'first_name': {'type': 'string', 'example': 'John'},
                'last_name': {'type': 'string', 'example': 'Doe'},
                'customer': {
                    'type': 'object',
                    'nullable': True,
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'address': {'type': 'string'},
                        'city': {'type': 'string'},
                        'state': {'type': 'string'},
                        'postal_code': {'type': 'string'},
                        'country': {'type': 'string'}
                    }
                }
            }
        },
        401: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'example': 'Authentication credentials were not provided.'}
            }
        }
    },
    summary='Get current user profile',
    description='Returns the authenticated user\'s profile information including linked customer details.'
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([ApiKeyPermission, IsAuthenticated])
def me_api(request):
    """Return current user profile with linked customer info."""
    user = request.user
    customer = None
    try:
        # Try by FK first if model has it; else by email fallback
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        if user.email:
            customer = Customer.objects.filter(email=user.email).first()

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'customer': CustomerSerializer(customer).data if customer else None,
    })


