#!/usr/bin/env python
"""
Task 3: Create Test Orders for BOTH Public and Private Users
Run with: python scripts/create_test_orders.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Product, Order, OrderItem, Cart

User = get_user_model()


def create_orders_for_user(user_email, user_password):
    """Helper to create 3 test orders for a specific user."""
    
    # 1. Get User
    user = User.objects.filter(email=user_email).first()
    if not user:
        print(f"❌ User {user_email} not found!")
        return False
    
    print(f"\n✅ Processing user: {user.username} ({user_email})")
    
    # 2. Get Products
    products = list(Product.objects.all()[:3])
    if len(products) < 1:
        print("❌ No products found! Run seed_public.py first.")
        return False
    
    # 3. Clear existing orders for this user (clean slate)
    count_deleted, _ = Order.objects.filter(user=user).delete()
    if count_deleted > 0:
        print(f"   🗑️  Cleared {count_deleted} existing orders")
    
    # 4. Create 3 Test Orders with different statuses/amounts
    test_data = [
        {'status': 'completed', 'qty_mult': 1},
        {'status': 'pending', 'qty_mult': 2},
        {'status': 'cancelled', 'qty_mult': 3},
    ]
    
    created_count = 0
    for i, data in enumerate(test_data):
        order = Order.objects.create(
            user=user,
            total_amount=0,
            status=data['status']
        )
        
        total = 0
        for product in products:
            quantity = (i + 1) * data['qty_mult']
            item_total = float(product.price) * quantity
            total += item_total
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )
        
        order.total_amount = total
        order.save()
        created_count += 1
        print(f"   ✅ Order #{i+1}: ID={order.id}, Status={order.status}, Amount=${total:.2f}")
    
    print(f"   🎉 Created {created_count} orders for {user.username}")
    return True


def main():
    print("="*60)
    print("Task 3: Creating Test Orders for ALL Users")
    print("="*60)
    
    users_to_process = [
        ('customer@public.com', 'PublicPass123!'),
        ('customer@private.com', 'PrivatePass123!'),
    ]
    
    success_count = 0
    for email, password in users_to_process:
        if create_orders_for_user(email, password):
            success_count += 1
    
    print("\n" + "="*60)
    print(f"✅ SUCCESS! Processed {success_count}/{len(users_to_process)} users.")
    print("="*60)
    


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)