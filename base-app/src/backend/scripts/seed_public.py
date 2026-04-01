import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Django setup failed! {e}")
    print(f"Current Path: {sys.path}")
    sys.exit(1)

try:
    # ✅ ADDED Coupon TO IMPORTS
    from api.models import User, Product, Profile, Order, OrderItem, Coupon
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    print("✅ Models imported successfully!")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not import models! {e}")
    print(f"Available models: {dir()}")
    sys.exit(1)

def seed_data():
    print("\n🌱 === STARTING COMPREHENSIVE SEED (Tasks 5, 6, 7) ===")
    
    users_to_create = [
        {"username": "admin_public", "email": "admin@public.com", "pwd": "AdminPass123!", "role": "admin", "is_staff": True},
        {"username": "vendor_public", "email": "vendor@public.com", "pwd": "VendorPass123!", "role": "vendor", "is_staff": False},
        {"username": "customer_public", "email": "customer@public.com", "pwd": "PublicPass123!", "role": "customer", "is_staff": False},
    ]

    created_users = {}

    # 1. Create Users & Profiles
    for u_data in users_to_create:
        user, created = User.objects.get_or_create(username=u_data["username"])
        
        user.set_password(u_data["pwd"])
        user.email = u_data["email"]
        user.is_staff = u_data.get("is_staff", False)
        user.save()
        
        # ✅ Ensure Profile exists with correct role
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = u_data["role"]
        profile.save()
        
        status = "Created" if created else "Updated"
        print(f"   ✅ {status} User: {u_data['username']} ({u_data['role']})")
        created_users[u_data["role"]] = user

    # 2. Create Products
    print("\n   📦 Creating Products (Owned by Vendor for Task 7)...")
    
    vendor = created_users.get("vendor")
    if not vendor:
        print("   ⚠️ Warning: Vendor user not found! Trying to fetch any user...")
        vendor = User.objects.filter(profile__role='vendor').first()
        if not vendor:
            print("   ❌ ERROR: No vendor user available to assign products!")
            return

    # ✅ FIXED: Changed to List of Dictionaries so we can access ['title'] and ['price']
    products_list = [
        {"title": "Premium Wireless Headphones", "price": "99.00"},
        {"title": "Mechanical Gaming Keyboard", "price": "89.50"},
        {"title": "4K Ultra HD Monitor", "price": "299.99"},
        {"title": "Ergonomic Office Chair", "price": "150.00"},
        {"title": "USB-C Hub Adapter", "price": "25.99"}
    ]

    created_products = []
    count = 0 # ✅ FIXED: Initialize counter
    
    for p_data in products_list:
        obj, created = Product.objects.get_or_create(
            title=p_data["title"],
            defaults={
                "price": p_data["price"],
                "description": f"High quality {p_data['title']} for sale.",
                "vendor": vendor,  # ✅ CRITICAL FOR TASK 7: Assign to Vendor
                "file_url": "https://via.placeholder.com/300?text=" + p_data["title"].replace(" ", "+")
            }
        )
        if created:
            count += 1
            print(f"      ➕ Created: {p_data['title']}")
        else:
            print(f"      ⏭️  Exists: {p_data['title']}")
        created_products.append(obj)

    # 3. TASK 6: Create Completed Order for Customer
    print("\n   🛒 Creating Completed Order for Review Testing (Task 6)...")
    customer = created_users.get("customer")
    
    if customer and created_products:
        existing_order = Order.objects.filter(user=customer, status='completed').first()
        
        if not existing_order:
            product = created_products[0]
            
            order = Order.objects.create(
                user=customer,
                total_amount=Decimal(product.price),
                status='completed'
            )
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1
            )
            print(f"      ✅ Created completed order for {customer.username}")
        else:
            print(f"      ⏭️  Completed order already exists")
    else:
        print("      ⚠️  Could not create order")

    # 4. TASK 5: Create Coupons
    print("\n   🎟️  Creating Coupons (Task 5)...")
    
    coupons_data = [
        {"code": "WELCOME10", "percent": 10.00, "min": 0, "days": 365},
        {"code": "EXPIRED20", "percent": 20.00, "min": 0, "days": -1},
        {"code": "BIG50", "percent": 50.00, "min": 100.00, "days": 365},
    ]

    for c_data in coupons_data:
        expires = timezone.now() + timedelta(days=c_data["days"])
        Coupon.objects.get_or_create(
            code=c_data["code"],
            defaults={
                "discount_percent": c_data["percent"],
                "min_order_amount": c_data["min"],
                "expires_at": expires,
                "is_active": True
            }
        )
        print(f"      ✅ Coupon: {c_data['code']}")

    # Summary
    print(f"\n🎉 === SEED COMPLETE ===")
    print(f"   Total Users: {User.objects.count()}")
    print(f"   Total Profiles: {Profile.objects.count()}")
    print(f"   Total Products: {Product.objects.count()} (All owned by 'vendor_public')")
    print(f"   Total Orders: {Order.objects.count()}")
    print(f"   Total Coupons: {Coupon.objects.count()}")
    print(f"   New Products Added: {count}") # ✅ FIXED: Now uses defined variable
    
    print("\n   🔑 Login Credentials:")
    print(f"   👤 Admin:    admin@public.com / AdminPass123!")
    print(f"   🏪 Vendor:   vendor@public.com / VendorPass123!  <-- Use for Task 7")
    print(f"   🛒 Customer: customer@public.com / PublicPass123! <-- Use for Task 5 & 6")
    print("========================\n")

if __name__ == "__main__":
    print("🚀 Script started...")
    try:
        seed_data()
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()