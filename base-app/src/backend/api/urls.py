from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    health_check,
    search_products,
    user_avatar_view, 
    ContactSupportView,
    LoginView,
    SignupView,
    LogoutView,
    UserProfileView,
    ProductViewSet,
    CartView,
    OrderViewSet,
    
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('products/search/', search_products, name='search-products'),
    path('user/avatar/', user_avatar_view, name='user-avatar'),
    path('contact/', ContactSupportView.as_view(), name='contact-support'),
    path('cart/', CartView.as_view(), name='cart'),
    path('', include(router.urls)),
]