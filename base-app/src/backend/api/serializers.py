from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Cart, Profile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_role(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.role if profile else 'customer'
    
    def get_avatar(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.avatar and hasattr(profile.avatar, 'url'):
            return profile.avatar.url
        return None


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'file_url', 'vendor', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'quantity', 'license_key']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'items', 'created_at']
        read_only_fields = ['id', 'created_at']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
        read_only_fields = ['id', 'created_at']