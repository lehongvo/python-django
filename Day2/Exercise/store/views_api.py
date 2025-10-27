from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Product, Category, Order, OrderItem, Customer
from .serializers import (
    ProductSerializer, CategorySerializer,
    OrderSerializer, OrderItemSerializer
)
from django.db.models import Q


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
def add_to_cart(request):
    """Add product to shopping cart"""
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
    
    # For now, return success (implement cart logic later)
    return Response({
        'message': f'Added {quantity} x {product.name} to cart',
        'product': ProductSerializer(product).data,
        'quantity': quantity,
        'total': float(product.price) * quantity
    })


@api_view(['POST'])
def buy_now(request):
    """Buy product immediately"""
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

