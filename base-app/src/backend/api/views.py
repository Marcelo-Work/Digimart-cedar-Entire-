from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import json
import os
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes

from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Q
from .models import User, Product, Order, OrderItem, Cart, Profile
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, CartSerializer
from .models import Coupon
from .serializers import CouponSerializer
from decimal import Decimal
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session authentication without CSRF enforcement for API endpoints"""
    def enforce_csrf(self, request):
        return  # Skip CSRF check
def health_check(request):
    return JsonResponse({'status': 'healthy'}, status=200)


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
            if hasattr(user, 'role'): user.role = 'customer'
            user.save()
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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        qs = Product.objects.all()
        search = self.request.query_params.get('q')
        if search: qs = qs.filter(title__icontains=search)
        return qs


@method_decorator(csrf_exempt, name='dispatch')
class CartView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request)
    def get(self, request):
        """Get current user's cart with calculated totals"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Calculate Raw Total from items
        raw_total = Decimal('0.00')
        for item in cart.items:
            try:
                product = Product.objects.get(id=item['product_id'])
                raw_total += Decimal(str(product.price)) * Decimal(str(item['quantity']))
            except: pass

        # Apply Coupon Logic
        discount = Decimal('0.00')
        applied_code = None
        
        if cart.coupon_code:
            try:
                coupon = Coupon.objects.get(code=cart.coupon_code)
                if coupon.is_valid() and raw_total >= coupon.min_order_amount:
                    discount = raw_total * (coupon.discount_percent / Decimal('100'))
                    applied_code = coupon.code
                else:
                    # Invalid coupon, clear it
                    cart.coupon_code = None
                    cart.discount_amount = Decimal('0.00')
                    cart.save()
            except Coupon.DoesNotExist:
                cart.coupon_code = None
                cart.save()

        final_total = raw_total - discount

        # Serialize manually to include calculated fields
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
        """Add item to cart"""
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'Product ID required'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        # Get or Create Cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check if item already exists in cart
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
        # Clear coupon if cart contents change (optional but good practice)
        cart.coupon_code = None
        cart.discount_amount = Decimal('0.00')
        cart.save()

        # Return updated cart
        return self.get(request)

    def patch(self, request):
        """Handle coupon application/removal"""
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
                
                # Calculate raw total
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
        """Clear cart"""
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items = []
            cart.coupon_code = None
            cart.discount_amount = Decimal('0.00')
            cart.save()
        return self.get(request)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Task 3: Order History with Sorting and Filtering
    GET /api/orders/?sort=created_at|total_amount|status&order=asc|desc&status=pending|completed|cancelled
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get orders for current user with sorting and filtering"""
        qs = Order.objects.filter(user=self.request.user)
        
        # Get sort parameters from query string
        sort_by = self.request.query_params.get('sort', 'created_at')
        order = self.request.query_params.get('order', 'desc')
        status_filter = self.request.query_params.get('status', '')
        
        # Validate sort field (security: prevent SQL injection)
        valid_sort_fields = ['created_at', 'total_amount', 'status']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        # Apply ordering
        if order == 'asc':
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by(f'-{sort_by}')
        
        # Apply status filter
        if status_filter:
            valid_statuses = ['pending', 'completed', 'cancelled']
            if status_filter in valid_statuses:
                qs = qs.filter(status=status_filter)
        
        return qs
    
    def create(self, request):
        """Create new order from cart"""
        cart = Cart.objects.get(user=request.user)
        if not cart.items:
            return Response({'error': 'Cart is empty'}, status=400)
        
        total = 0
        order = Order.objects.create(user=request.user, total_amount=0, status='completed')
        
        for item in cart.items:
            product = Product.objects.get(id=item['product_id'])
            total += float(product.price) * item['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])
        
        order.total_amount = total
        order.save()
        cart.items = []
        cart.save()
        
        return Response(OrderSerializer(order).data, status=201)
    
    def list(self, request):
        """List orders with sorting (explicit override for clarity)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_products(request):
    """
    Dedicated search endpoint: GET /api/products/search/?q=keyword
    Searches title AND description.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        # If no query, return empty list or all products (depending on requirement)
        # Usually for search bars, if empty, we return empty or let frontend handle 'all'
        products = Product.objects.none() 
    else:
        products = Product.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    # Manual serialization to match the exact structure expected by frontend/tests
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
    """
    Handles contact form submission with server-side validation.
    Accessible to guests and authenticated users.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Disable authentication to bypass CSRF enforcement
    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        errors = {}

        # 1. Validate Name
        if not name:
            errors['name'] = 'Name is required.'

        # 2. Validate Email
        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'

        # 3. Validate Subject
        if not subject:
            errors['subject'] = 'Subject is required.'

        # 4. Validate Message (Length 10-500)
        if not message:
            errors['message'] = 'Message is required.'
        else:
            if len(message) < 10:
                errors['message'] = 'Message must be at least 10 characters long.'
            elif len(message) > 500:
                errors['message'] = 'Message must not exceed 500 characters.'

        # If errors exist, return them
        if errors:
            return Response({'errors': errors}, status=400)

        # ✅ Success
        return Response({
            'success': True,
            'message': 'Your message has been sent successfully!'
        }, status=200)

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

    # 1. Check Active & Expiry
    if not coupon.is_valid():
        if coupon.expires_at and timezone.now() > coupon.expires_at:
            return Response({'error': 'This coupon has expired'}, status=400)
        return Response({'error': 'This coupon is no longer active'}, status=400)

    # 2. Check Minimum Order Amount
    if cart_total < coupon.min_order_amount:
        return Response({
            'error': f'Minimum order amount for this coupon is ${coupon.min_order_amount}'
        }, status=400)

    # 3. Calculate Discount
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