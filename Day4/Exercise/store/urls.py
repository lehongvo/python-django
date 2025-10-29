from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('account/orders/', views.account_orders, name='account_orders'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/addresses/', views.account_addresses, name='account_addresses'),
    path('logout/', views.logout_view, name='logout'),
    path('track-order/', views.order_tracking, name='order_tracking'),
    # Support pages
    path('support/help-center/', views.help_center, name='help_center'),
    path('support/contact/', views.contact_us, name='contact_us'),
    path('support/shipping/', views.shipping_info, name='shipping_info'),
    path('support/returns/', views.returns_policy, name='returns_policy'),
]


