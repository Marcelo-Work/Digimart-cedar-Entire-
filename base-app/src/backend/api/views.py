import json
import os
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, Product, Order, OrderItem, Cart, Profile
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, CartSerializer


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


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items
        product_id = request.data.get('product_id')
        if not any(item['product_id'] == product_id for item in items):
            items.append({'product_id': product_id, 'quantity': 1})
            cart.items = items
            cart.save()
        return Response(CartSerializer(cart).data)
    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.query_params.get('product_id')
        cart.items = [i for i in cart.items if i['product_id'] != product_id]
        cart.save()
        return Response(CartSerializer(cart).data)


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
    query = request.query_params.get('q', '')
    if query:
        products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.all()
    data = [{"id": p.id, "title": p.title, "price": str(p.price), "description": p.description, "file_url": p.file_url, "vendor": p.vendor.username if p.vendor else None} for p in products]
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
