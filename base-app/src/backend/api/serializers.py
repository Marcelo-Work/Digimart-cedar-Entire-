from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Cart, Coupon


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
        read_only_fields = ['id', 'created_at','user']


class CartSerializer(serializers.ModelSerializer):

    raw_total = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()
    applied_coupon = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'raw_total', 'discount_amount', 'final_total', 'applied_coupon']
        read_only_fields = ['id', 'created_at']

    def get_raw_total(self, obj):
        total = 0.0
        for item in obj.items:
            try:
                product = Product.objects.get(id=item['product_id'])
                total += float(product.price) * item['quantity']
            except: pass
        return total

    def get_discount_amount(self, obj):
        return float(obj.discount_amount) if obj.discount_amount else 0.0

    def get_final_total(self, obj):
        raw = self.get_raw_total(obj)
        discount = self.get_discount_amount(obj)
        return raw - discount

    def get_applied_coupon(self, obj):
        return obj.coupon_code if obj.coupon_code else None

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_percent', 'min_order_amount', 'expires_at', 'is_active']
        read_only_fields = ['id', 'created_at']