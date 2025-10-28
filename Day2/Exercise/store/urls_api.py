from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_api import ProductViewSet, CategoryViewSet, add_to_cart, buy_now, order_detail, cart_sync, cart_clear

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('cart/add/', add_to_cart, name='cart_add'),
    path('cart/sync/', cart_sync, name='cart_sync'),
    path('cart/clear/', cart_clear, name='cart_clear'),
    path('buy-now/', buy_now, name='buy_now'),
    path('orders/<str:order_number>/', order_detail, name='order_detail'),
] + router.urls

