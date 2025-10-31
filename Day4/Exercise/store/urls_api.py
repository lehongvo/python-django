from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_api import (
    ProductViewSet, CategoryViewSet,
    add_to_cart, buy_now, order_detail, my_orders,
    cart_sync, cart_clear,
    cart_list, cart_update, cart_remove,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views_auth_api import register_api, me_api

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Auth endpoints (JWT)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', register_api, name='auth_register'),
    path('auth/me/', me_api, name='auth_me'),
    path('cart/add/', add_to_cart, name='cart_add'),
    path('cart/list/', cart_list, name='cart_list'),
    path('cart/update/', cart_update, name='cart_update'),
    path('cart/remove/', cart_remove, name='cart_remove'),
    path('cart/sync/', cart_sync, name='cart_sync'),
    path('cart/clear/', cart_clear, name='cart_clear'),
    path('buy-now/', buy_now, name='buy_now'),
    path('orders/my/', my_orders, name='orders_my'),
    path('orders/<str:order_number>/', order_detail, name='order_detail'),
] + router.urls

