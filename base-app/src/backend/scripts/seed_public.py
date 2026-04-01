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
    from api.models import User, Product, Profile, Order, OrderItem
    print("✅ Models imported successfully!")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not import models! {e}")
    print(f"Available models: {dir()}")
    sys.exit(1)

def seed_data():
    print("\n🌱 === STARTING PUBLIC SEED ===")
    
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
    print("\n   📦 Creating Products...")
    
    vendor = created_users.get("vendor")
    if not vendor:
        print("   ⚠️ Warning: Vendor user not found! Trying to fetch any user...")
        vendor = User.objects.filter(profile__role='vendor').first()
        if not vendor:
            print("   ❌ ERROR: No vendor user available to assign products!")
            return

    products_list = [
        "Premium Wireless Headphones",
        "Mechanical Gaming Keyboard",
        "4K Ultra HD Monitor",
        "Ergonomic Office Chair",
        "USB-C Hub Adapter"
    ]

    count = 0
    created_products = []
    
    for title in products_list:
        obj, created = Product.objects.get_or_create(
            title=title,
            defaults={
                "price": "99.00",
                "description": f"High quality {title} for sale.",
                "vendor": vendor,
                "file_url": "https://via.placeholder.com/300?text=" + title.replace(" ", "+")
            }
        )
        if created:
            count += 1
            print(f"      ➕ Created: {title}")
        else:
            print(f"      ⏭️  Exists: {title}")
        created_products.append(obj)

    # 3. ✅ TASK 6: Create Completed Order for Customer
    # This allows the customer to write reviews
    print("\n   🛒 Creating Completed Order for Review Testing...")
    customer = created_users.get("customer")
    
    if customer and created_products:
        # Check if order already exists to avoid duplicates
        existing_order = Order.objects.filter(user=customer, status='completed').first()
        
        if not existing_order:
            product = created_products[0] # Use first product
            
            # Create Order
            order = Order.objects.create(
                user=customer,
                total_amount=product.price,
                status='completed' # MUST be completed to allow review
            )
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1
            )
            print(f"      ✅ Created completed order for {customer.username} (Product: {product.title})")
        else:
            print(f"      ⏭️  Completed order already exists for {customer.username}")
    else:
        print("      ⚠️  Could not create order (missing customer or products)")

    print(f"\n🎉 === SEED COMPLETE ===")
    print(f"   Total Users: {User.objects.count()}")
    print(f"   Total Profiles: {Profile.objects.count()}")
    print(f"   Total Products: {Product.objects.count()}")
    print(f"   Total Orders: {Order.objects.count()}")
    print(f"   New Products Added: {count}")
    print("\n   📝 Task 6 Ready: Customer can now review 'Premium Wireless Headphones'")
    print("   🔑 Login: customer@public.com / PublicPass123!")
    print("========================\n")

if __name__ == "__main__":
    print("🚀 Script started...")
    try:
        seed_data()
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()