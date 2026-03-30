from rest_framework import serializers
from .models import User, Product, Order, OrderItem, Cart

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
       
        fields = ['id', 'username', 'email', 'role', 'avatar']
        read_only_fields = ['id']

class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'file_url', 'vendor', 'vendor_name', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_title', 'quantity', 'license_key']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'user_name', 'total_amount', 'status', 'items', 'created_at']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'updated_at']