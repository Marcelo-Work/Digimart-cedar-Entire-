import os, sys, django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Coupon
from datetime import timedelta
from django.utils import timezone

print("Seeding Coupons...")

# 1. Valid 10% Off (No minimum)
Coupon.objects.get_or_create(
    code='WELCOME10',
    defaults={
        'discount_percent': 10.00,
        'min_order_amount': 0.00,
        'expires_at': timezone.now() + timedelta(days=365),
        'is_active': True
    }
)

# 2. Expired Coupon
Coupon.objects.get_or_create(
    code='EXPIRED20',
    defaults={
        'discount_percent': 20.00,
        'min_order_amount': 0.00,
        'expires_at': timezone.now() - timedelta(days=1),
        'is_active': True
    }
)

# 3. High Threshold ($100 min)
Coupon.objects.get_or_create(
    code='BIG50',
    defaults={
        'discount_percent': 50.00,
        'min_order_amount': 100.00,
        'expires_at': timezone.now() + timedelta(days=365),
        'is_active': True
    }
)

print("✅ Coupons seeded: WELCOME10, EXPIRED20, BIG50")