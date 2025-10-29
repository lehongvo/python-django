from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Category, Tag, Product, Customer, Order, OrderItem, Cart


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'stock', 'status', 'is_featured', 'created_at'
    ]
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['tags']
    list_per_page = 25
    actions = ['make_published', 'make_featured', 'mark_out_of_stock']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Inventory', {
            'fields': ('stock', 'sku')
        }),
        ('Relations', {
            'fields': ('category', 'tags')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
    )
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} products marked as published.')
    make_published.short_description = 'Mark selected products as published'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products marked as featured.')
    make_featured.short_description = 'Mark selected products as featured'
    
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(status='out_of_stock')
        self.message_user(request, f'{updated} products marked as out of stock.')
    mark_out_of_stock.short_description = 'Mark selected products as out of stock'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'city', 'country', 'created_at']
    list_filter = ['country', 'state', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'customer__name', 'customer__email']
    readonly_fields = ['order_number', 'order_date', 'updated_at', 'total_amount']
    inlines = [OrderItemInline]
    actions = ['mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_amount')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address', 'shipping_city', 'shipping_state',
                'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Timestamps', {
            'fields': ('order_date', 'updated_at')
        }),
    )
    
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_processing.short_description = 'Mark selected orders as processing'
    
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_shipped.short_description = 'Mark selected orders as shipped'
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = 'Mark selected orders as delivered'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as cancelled.')
    mark_cancelled.short_description = 'Mark selected orders as cancelled'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__order_number', 'product__name']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['customer__name', 'customer__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']


# Customize Admin Site
admin.site.site_header = "TechStore 2025 - Admin Panel"
admin.site.site_title = "TechStore Admin"
admin.site.index_title = "Welcome to TechStore Administration"



