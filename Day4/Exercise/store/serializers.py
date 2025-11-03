from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Product, Category, Tag, Order, OrderItem, Customer


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Category Example',
            value={
                'id': 10,
                'name': 'Laptops',
                'slug': 'laptops',
                'description': 'Portable computers',
                'is_active': True,
            }
        )
    ]
)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active']
        extra_kwargs = {
            'name': {'help_text': 'Display name of the category'},
            'slug': {'help_text': 'URL-friendly unique identifier'},
            'description': {'help_text': 'Optional description'},
            'is_active': {'help_text': 'Whether this category is visible'},
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Product Example',
            value={
                'id': 101,
                'name': 'MacBook Pro 14',
                'slug': 'macbook-pro-14',
                'description': 'High‑performance laptop',
                'short_description': 'M3 Pro, 16GB RAM, 512GB',
                'price': '1999.00',
                'compare_price': '2199.00',
                'stock': 25,
                'sku': 'MBP14-2025',
                'category': {
                    'id': 10, 'name': 'Laptops', 'slug': 'laptops', 'description': 'Portable computers', 'is_active': True
                },
                'tags': [{'id': 1, 'name': 'Apple', 'slug': 'apple'}],
                'status': 'published',
                'is_featured': True,
                'created_at': '2025-01-01T12:00:00Z',
                'updated_at': '2025-01-05T12:00:00Z'
            }
        )
    ]
)
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True, source='category')
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'price', 'compare_price', 'stock', 'sku',
            'category', 'category_id', 'tags',
            'status', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['sku', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'help_text': 'Product name'},
            'slug': {'help_text': 'URL slug (unique)'},
            'description': {'help_text': 'Full product description'},
            'short_description': {'help_text': 'Short summary for listings'},
            'price': {'help_text': 'Current sale price'},
            'compare_price': {'help_text': 'Strikethrough/old price for comparison'},
            'stock': {'help_text': 'Inventory units available'},
            'status': {'help_text': "Publication status: 'draft' | 'published' | 'out_of_stock'"},
            'is_featured': {'help_text': 'Show in featured sections'},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'OrderItem Example',
            value={'id': 1, 'product': {'id': 101, 'name': 'MacBook Pro 14', 'slug': 'macbook-pro-14'}, 'quantity': 2, 'price': '1999.00', 'subtotal': '3998.00'}
        )
    ]
)
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'subtotal']
        extra_kwargs = {
            'quantity': {'help_text': 'Units purchased'},
            'price': {'help_text': 'Unit price at time of order'},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Customer Example',
            value={
                'id': 7,
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1 555-1234',
                'address': '1 Market St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94105',
                'country': 'USA',
                'created_at': '2025-01-01T12:00:00Z',
                'updated_at': '2025-01-05T12:00:00Z'
            }
        )
    ]
)
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address',
            'city', 'state', 'postal_code', 'country',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'name': {'help_text': 'Full name of customer'},
            'email': {'help_text': 'Contact email'},
            'phone': {'help_text': 'Phone number'},
            'address': {'help_text': 'Street address'},
            'postal_code': {'help_text': 'ZIP/Postal code'},
            'country': {'help_text': 'Country/Region'},
        }


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Order Example',
            value={
                'id': 5001,
                'order_number': 'TS-2025-00001',
                'customer': {'id': 7, 'name': 'John Doe', 'email': 'john@example.com'},
                'status': 'processing',
                'total_amount': '3998.00',
                'shipping_address': '1 Market St',
                'shipping_city': 'San Francisco',
                'shipping_state': 'CA',
                'shipping_postal_code': '94105',
                'shipping_country': 'USA',
                'order_date': '2025-01-01T12:00:00Z',
                'updated_at': '2025-01-05T12:00:00Z',
                'items': []
            }
        )
    ]
)
class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), write_only=True, source='customer')
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_id',
            'status', 'total_amount',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country',
            'order_date', 'updated_at',
            'items'
        ]
        read_only_fields = ['order_number', 'order_date', 'updated_at', 'total_amount']
        extra_kwargs = {
            'status': {'help_text': "Order status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled'"},
            'shipping_address': {'help_text': 'Recipient address'},
        }


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

