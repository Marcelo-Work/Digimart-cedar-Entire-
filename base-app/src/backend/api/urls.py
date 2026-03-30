from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, SignupView,LogoutView, ProductViewSet, CartView, OrderViewSet, UserProfileView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', UserProfileView.as_view(), name='profile'),
    path('cart/', CartView.as_view(), name='cart'),
    path('', include(router.urls)),
]