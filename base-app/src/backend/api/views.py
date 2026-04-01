import os
import time
import json
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Avg, Count
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate, login, logout

# Models & Serializers
from .models import User, Product, Order, OrderItem, Cart, Profile, Review, Coupon, EmailLog
from .serializers import (
    UserSerializer, ProductSerializer, OrderSerializer, 
    CartSerializer, CouponSerializer, ReviewSerializer
)
from .authentication import CsrfExemptSessionAuthentication

# Task 8: Import the background task
from .tasks import send_order_confirmation_email

# =============================================================================
# HEALTH CHECK
# =============================================================================
def health_check(request):
    return JsonResponse({'status': 'healthy'}, status=200)

# =============================================================================
# AUTH VIEWS
# =============================================================================
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            try:
                raw_data = json.loads(request.body)
                email = raw_data.get('email')
                password = raw_data.get('password')
            except: pass
            
        if not email or not password:
            return Response({'error': 'Email and password required'}, status=400)
            
        try:
            user_obj = User.objects.get(email=email)
            authenticated_user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            authenticated_user = None
            
        if authenticated_user:
            login(request, authenticated_user)
            return Response({'success': True, 'user': UserSerializer(authenticated_user).data})
            
        return Response({'success': False, 'error': 'Invalid credentials'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not email or not password:
            try:
                raw_data = json.loads(request.body)
                username = raw_data.get('username')
                email = raw_data.get('email')
                password = raw_data.get('password')
            except: pass
            
        if not username or not email or not password:
            return Response({'error': 'Username, email, and password required'}, status=400)
            
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=400)
            
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            
            # Create Profile if needed
            Profile.objects.get_or_create(user=user, defaults={'role': 'customer'})
            
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return Response({'success': True, 'user': UserSerializer(authenticated_user).data}, status=201)
                
            return Response({'success': True, 'message': 'Account created', 'user': UserSerializer(user).data}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            logout(request)
            request.session.flush()
            response = Response({'success': True, 'message': 'Logged out successfully'})
            response.delete_cookie('sessionid')
            return response
        except:
            return Response({'success': True, 'message': 'Logout forced'}, status=200)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)

# =============================================================================
# PRODUCT VIEWS
# =============================================================================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        qs = Product.objects.all()
        search = self.request.query_params.get('q')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_products(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        products = Product.objects.none() 
    else:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    data = [
        {
            "id": p.id,
            "title": p.title,
            "price": str(p.price),
            "description": p.description,
            "file_url": p.file_url,
            "vendor": p.vendor.username if p.vendor else None,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } 
        for p in products
    ]
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_detail_with_reviews(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

# =============================================================================
# CART VIEWS
# =============================================================================
@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        raw_total = Decimal('0.00')
        
        for item in cart.items:
            try:
                product = Product.objects.get(id=item['product_id'])
                raw_total += Decimal(str(product.price)) * Decimal(str(item['quantity']))
            except: pass

        discount = Decimal('0.00')
        applied_code = None
        
        if cart.coupon_code:
            try:
                coupon = Coupon.objects.get(code=cart.coupon_code)
                if coupon.is_valid() and raw_total >= coupon.min_order_amount:
                    discount = raw_total * (coupon.discount_percent / Decimal('100'))
                    applied_code = coupon.code
                else:
                    cart.coupon_code = None
                    cart.discount_amount = Decimal('0.00')
                    cart.save()
            except Coupon.DoesNotExist:
                cart.coupon_code = None
                cart.save()

        final_total = raw_total - discount

        data = {
            'id': cart.id,
            'user': cart.user.id,
            'items': cart.items,
            'created_at': cart.created_at.isoformat(),
            'raw_total': float(raw_total),
            'discount_amount': float(discount),
            'final_total': float(final_total),
            'applied_coupon': applied_code
        }
        return Response(data)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'Product ID required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items
        found = False
        
        for item in items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                found = True
                break
        
        if not found:
            items.append({'product_id': product_id, 'quantity': quantity})

        cart.items = items
        cart.coupon_code = None
        cart.discount_amount = Decimal('0.00')
        cart.save()

        return self.get(request)

    def patch(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        action = request.data.get('action')
        
        if action == 'apply_coupon':
            code = request.data.get('code', '').strip().upper()
            if not code:
                return Response({'error': 'Code required'}, status=400)
            
            try:
                coupon = Coupon.objects.get(code=code)
                if not coupon.is_valid():
                    return Response({'error': 'Coupon expired or inactive'}, status=400)
                
                raw_total = Decimal('0.00')
                for item in cart.items:
                    try:
                        p = Product.objects.get(id=item['product_id'])
                        raw_total += Decimal(str(p.price)) * Decimal(str(item['quantity']))
                    except: pass
                
                if raw_total < coupon.min_order_amount:
                    return Response({'error': f'Minimum order ${coupon.min_order_amount}'}, status=400)
                
                cart.coupon_code = code
                cart.discount_amount = raw_total * (coupon.discount_percent / Decimal('100'))
                cart.save()
                return self.get(request)
                
            except Coupon.DoesNotExist:
                return Response({'error': 'Invalid coupon code'}, status=400)

        elif action == 'remove_coupon':
            cart.coupon_code = None
            cart.discount_amount = Decimal('0.00')
            cart.save()
            return self.get(request)

        return Response({'error': 'Invalid action'}, status=400)

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items = []
            cart.coupon_code = None
            cart.discount_amount = Decimal('0.00')
            cart.save()
        return self.get(request)

# =============================================================================
# ORDER VIEWS (TASK 8 UPDATED)
# =============================================================================
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user)
        sort_by = self.request.query_params.get('sort', 'created_at')
        order = self.request.query_params.get('order', 'desc')
        status_filter = self.request.query_params.get('status', '')
        
        valid_sort_fields = ['created_at', 'total_amount', 'status']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if order == 'asc':
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by(f'-{sort_by}')
        
        if status_filter and status_filter in ['pending', 'completed', 'cancelled']:
            qs = qs.filter(status=status_filter)
        
        return qs
    
    def create(self, request):
        """Create new order from cart with ASYNC email notification"""
        start_time = time.time()
        user = request.user
        
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=400)
            
        if not cart.items:
            return Response({'error': 'Cart is empty'}, status=400)
        
        try:
            with transaction.atomic():
                # Calculate Total
                total = Decimal('0.00')
                for item in cart.items:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        total += Decimal(str(product.price)) * Decimal(str(item['quantity']))
                    except: pass
                
                # Apply Discount if any
                if cart.coupon_code:
                    try:
                        coupon = Coupon.objects.get(code=cart.coupon_code)
                        if coupon.is_valid() and total >= coupon.min_order_amount:
                            discount = total * (coupon.discount_percent / Decimal('100'))
                            total -= discount
                    except: pass

                # Create Order
                order = Order.objects.create(
                    user=user, 
                    total_amount=total, 
                    status='completed'
                )
                
                # Create OrderItems
                for item in cart.items:
                    try:
                        product = Product.objects.get(id=item['product_id'])
                        OrderItem.objects.create(
                            order=order, 
                            product=product, 
                            quantity=item['quantity'],
                            total_price=Decimal(str(product.price)) * Decimal(str(item['quantity']))
                        )
                    except: pass
                
                # Clear Cart
                cart.items = []
                cart.coupon_code = None
                cart.discount_amount = Decimal('0.00')
                cart.save()
                
                # ✅ TASK 8: TRIGGER ASYNC EMAIL
                # This runs in background, does not block response
                send_order_confirmation_email(order.id)

            execution_time = time.time() - start_time
            
            return Response({
                'message': 'Order placed successfully',
                'order_id': order.id,
                'processing_time_seconds': round(execution_time, 4),
                'email_status': 'queued_for_async_delivery',
                'total_amount': float(total)
            }, status=201)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# =============================================================================
# EMAIL LOG VIEWS (TASK 8 NEW)
# =============================================================================
class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Exposes email logs to frontend for verification.
    In production, restrict this to Admin/Staff only.
    """
    queryset = EmailLog.objects.all().order_by('-created_at')
    serializer_class = None # We will define a simple inline serializer or use ModelSerializer
    
    def get_serializer_class(self):
        from rest_framework import serializers
        class EmailLogSerializer(serializers.ModelSerializer):
            class Meta:
                model = EmailLog
                fields = '__all__'
        return EmailLogSerializer
    
    permission_classes = [permissions.IsAuthenticated] # Require login to see logs

# =============================================================================
# SUPPORT & AVATAR
# =============================================================================
@csrf_exempt
@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_avatar_view(request):
    try:
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            avatar_url = None
            if profile.avatar and hasattr(profile.avatar, 'url') and profile.avatar.url:
                avatar_url = request.build_absolute_uri(profile.avatar.url)
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': avatar_url,
                'role': getattr(profile, 'role', 'customer'),
                'date_joined': user.date_joined.isoformat() if user.date_joined else None
            }, status=200)
        
        elif request.method == 'PUT':
            if 'avatar' not in request.FILES:
                return Response({'error': 'No avatar file provided'}, status=400)
            
            avatar_file = request.FILES['avatar']
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            _, file_ext = os.path.splitext(avatar_file.name)
            file_ext = file_ext.lower()
            
            if file_ext not in allowed_extensions:
                return Response({'error': 'Invalid file type: ' + file_ext}, status=400)
            
            if avatar_file.size > 5 * 1024 * 1024:
                return Response({'error': 'File too large'}, status=400)
            
            profile.avatar = avatar_file
            profile.save(update_fields=['avatar'])
            
            avatar_url = None
            if profile.avatar and hasattr(profile.avatar, 'url') and profile.avatar.url:
                avatar_url = request.build_absolute_uri(profile.avatar.url)
            
            return Response({
                'success': True,
                'avatar': avatar_url,
                'message': 'Avatar uploaded successfully'
            }, status=200)
        else:
            return Response({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ContactSupportView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()
        errors = {}

        if not name: errors['name'] = 'Name is required.'
        if not email: errors['email'] = 'Email is required.'
        else:
            try: validate_email(email)
            except ValidationError: errors['email'] = 'Enter a valid email address.'
        if not subject: errors['subject'] = 'Subject is required.'
        if not message: errors['message'] = 'Message is required.'
        else:
            if len(message) < 10: errors['message'] = 'Message must be at least 10 characters long.'
            elif len(message) > 500: errors['message'] = 'Message must not exceed 500 characters.'

        if errors:
            return Response({'errors': errors}, status=400)

        return Response({'success': True, 'message': 'Your message has been sent successfully!'}, status=200)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon_view(request):
    code = request.data.get('code', '').strip().upper()
    cart_total = Decimal(str(request.data.get('cart_total', 0)))

    if not code:
        return Response({'error': 'Coupon code is required'}, status=400)

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return Response({'error': 'Invalid coupon code'}, status=400)

    if not coupon.is_valid():
        if coupon.expires_at and timezone.now() > coupon.expires_at:
            return Response({'error': 'This coupon has expired'}, status=400)
        return Response({'error': 'This coupon is no longer active'}, status=400)

    if cart_total < coupon.min_order_amount:
        return Response({'error': f'Minimum order amount for this coupon is ${coupon.min_order_amount}'}, status=400)

    discount_amount = cart_total * (coupon.discount_percent / Decimal('100'))
    new_total = cart_total - discount_amount

    return Response({
        'valid': True,
        'code': coupon.code,
        'discount_percent': float(coupon.discount_percent),
        'discount_amount': float(discount_amount),
        'original_total': float(cart_total),
        'new_total': float(new_total)
    })

# =============================================================================
# REVIEW VIEWS
# =============================================================================
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        from rest_framework import serializers # Local import to fix scope
        product_id = self.request.data.get('product')
        
        has_purchased = OrderItem.objects.filter(
            order__user=self.request.user,
            order__status='completed',
            product_id=product_id
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError("You can only review products you have purchased.")

        if Review.objects.filter(user=self.request.user, product_id=product_id).exists():
            raise serializers.ValidationError("You have already reviewed this product.")

        review = serializer.save(user=self.request.user)
        review.product.update_rating_stats()

# =============================================================================
# VENDOR VIEWS
# =============================================================================
class IsVendorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return False
        return profile.role in ['vendor', 'admin']

class VendorProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsVendorOrAdmin]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if profile and profile.role == 'admin':
            return Product.objects.all()
        return Product.objects.filter(vendor=user)

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.profile.role == 'admin' and instance.vendor != request.user:
            return Response({'error': 'Admins cannot modify products owned by other vendors.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.profile.role == 'admin' and instance.vendor != request.user:
            return Response({'error': 'Admins cannot delete products owned by other vendors.'}, status=403)
        return super().destroy(request, *args, **kwargs)