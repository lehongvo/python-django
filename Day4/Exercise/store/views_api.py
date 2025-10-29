from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Product, Category, Order, OrderItem, Customer, Cart
from .serializers import (
    ProductSerializer, CategorySerializer,
    OrderSerializer, OrderItemSerializer
)
from django.db.models import Q


def _get_or_create_customer_for_user(user):
    """Resolve a stable Customer for an authenticated user.
    Uses user.email if present; otherwise falls back to username-based synthetic email
    to avoid collisions between users with blank emails.
    """
    safe_email = user.email or f"{user.username}@example.com"
    # 1) Prefer existing customer linked by user
    try:
        return Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        pass

    # 2) If a customer already exists with this email and is unlinked, claim it
    try:
        existing_by_email = Customer.objects.get(email=safe_email)
        if existing_by_email.user_id in (None, user.id):
            existing_by_email.user = user
            # Ensure name present
            if not existing_by_email.name:
                existing_by_email.name = user.get_full_name() or user.username
            existing_by_email.save(update_fields=['user', 'name'])
            return existing_by_email
        # If email belongs to another user, synthesize unique email
        unique_email = f"{user.username}+{user.id}@example.com"
    except Customer.DoesNotExist:
        unique_email = safe_email

    # 3) Create new customer with unique email
    return Customer.objects.create(
        user=user,
        name=user.get_full_name() or user.username,
        email=unique_email,
        phone='',
        address='',
        city='',
        state='',
        postal_code='',
        country='USA',
    )


class ProductViewSet(viewsets.ModelViewSet):
    """Product API ViewSet"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.select_related('category').prefetch_related('tags')
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search products"""
        query = request.query_params.get('q', '')
        products = self.get_queryset().filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:20]
        serializer = self.get_serializer(products, many=True)
        return Response({
            'query': query,
            'results': serializer.data,
            'count': len(serializer.data)
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """Category API ViewSet"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Category.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in a category"""
        category = self.get_object()
        products = Product.objects.filter(category=category, status='published')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def add_to_cart(request):
    """Add product to shopping cart"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return Response(
            {
                'error': 'Please log in to add items to cart',
                'requires_login': True,
                'login_url': '/login/'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    if not product_id:
        return Response(
            {'error': 'Product ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if product.stock < quantity:
        return Response(
            {'error': 'Insufficient stock'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create customer (per-user mapping)
    customer = _get_or_create_customer_for_user(request.user)
    
    # Add or update cart item in database
    cart_item, created = Cart.objects.get_or_create(
        customer=customer,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already exists
        cart_item.quantity += quantity
        cart_item.save()
    
    # Return success
    return Response({
        'message': f'Added {quantity} x {product.name} to cart',
        'product': ProductSerializer(product).data,
        'quantity': cart_item.quantity,
        'total': float(product.price) * cart_item.quantity
    })


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def buy_now(request):
    """Buy product immediately"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return Response(
            {
                'error': 'Please log in to purchase products',
                'requires_login': True,
                'login_url': '/login/'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    if not product_id:
        return Response(
            {'error': 'Product ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if product.stock < quantity:
        return Response(
            {'error': 'Insufficient stock'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For now, return success (implement order creation later)
    return Response({
        'message': f'Proceeding to checkout for {product.name}',
        'product': ProductSerializer(product).data,
        'quantity': quantity,
        'total': float(product.price) * quantity,
        'redirect': f'/checkout/?product={product_id}&quantity={quantity}'
    })


@api_view(['GET'])
def order_detail(request, order_number):
    """Get order details by order number"""
    try:
        order = Order.objects.select_related('customer').prefetch_related('items__product').get(order_number=order_number)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def cart_sync(request):
    """Sync cart from localStorage to database"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Please log in to sync your cart'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get or create customer
    from django.contrib.auth.models import User
    customer = _get_or_create_customer_for_user(request.user)
    
    cart_data = request.data.get('cart', [])
    
    # Clear existing cart for this customer
    Cart.objects.filter(customer=customer).delete()
    
    # Add new cart items
    for item in cart_data:
        try:
            product = Product.objects.get(id=item['product_id'])
            Cart.objects.create(
                customer=customer,
                product=product,
                quantity=item['quantity']
            )
        except Product.DoesNotExist:
            pass
    
    return Response({'message': 'Cart synced successfully'})


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def cart_clear(request):
    """Clear cart for logged out user"""
    # Clear localStorage on client
    return Response({'message': 'Cart cleared'})


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
def cart_list(request):
    """Return current user's cart items from database"""
    if not request.user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    customer = _get_or_create_customer_for_user(request.user)

    items_qs = Cart.objects.filter(customer=customer).select_related('product')
    items = []
    subtotal = 0.0
    for ci in items_qs:
        price = float(ci.product.price)
        line_total = price * ci.quantity
        subtotal += line_total
        items.append({
            'product_id': ci.product.id,
            'name': ci.product.name,
            'price': price,
            'quantity': ci.quantity,
            'image': ci.product.image.url if getattr(ci.product, 'image', None) and ci.product.image else None,
            'subtotal': line_total,
        })

    return Response({
        'items': items,
        'count': sum(i['quantity'] for i in items),
        'subtotal': subtotal,
    })


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def cart_update(request):
    """Set quantity for a cart item in DB (add/update/remove)."""
    if not request.user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product_id')
    quantity = int(request.data.get('quantity', 1))
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    customer = _get_or_create_customer_for_user(request.user)

    if quantity <= 0:
        Cart.objects.filter(customer=customer, product=product).delete()
        return Response({'message': 'Item removed'})

    cart_item, _ = Cart.objects.get_or_create(customer=customer, product=product, defaults={'quantity': quantity})
    if cart_item.quantity != quantity:
        cart_item.quantity = quantity
        cart_item.save()

    return Response({'message': 'Cart updated', 'quantity': cart_item.quantity})


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
def cart_remove(request):
    """Remove an item from the cart in DB."""
    if not request.user.is_authenticated:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'message': 'Item already removed'})

    customer = _get_or_create_customer_for_user(request.user)

    Cart.objects.filter(customer=customer, product=product).delete()
    return Response({'message': 'Item removed'})

