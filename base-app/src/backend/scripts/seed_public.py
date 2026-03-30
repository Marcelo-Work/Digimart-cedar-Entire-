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
    from api.models import User, Product
    print("✅ Models imported successfully!")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not import models! {e}")
    sys.exit(1)

def seed_data():
    print("\n🌱 === STARTING PUBLIC SEED ===")
    
    users_to_create = [
        {"username": "admin_public", "email": "admin@public.com", "pwd": "AdminPass123!", "role": "admin", "is_staff": True},
        {"username": "vendor_public", "email": "vendor@public.com", "pwd": "VendorPass123!", "role": "vendor", "is_staff": False},
        {"username": "customer_public", "email": "customer@public.com", "pwd": "PublicPass123!", "role": "customer", "is_staff": False},
    ]

    created_users = {}

    for u_data in users_to_create:
        user, created = User.objects.get_or_create(username=u_data["username"])
        
        user.set_password(u_data["pwd"])
        user.email = u_data["email"]
        user.is_staff = u_data.get("is_staff", False)
        
        if hasattr(user, 'role'):
            user.role = u_data["role"]
        
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"   ✅ {status} User: {u_data['username']} ({u_data['role']})")
        created_users[u_data["role"]] = user

  
    print("\n   📦 Creating Products...")
    
    vendor = created_users.get("vendor")
    if not vendor:
        print("   ⚠️ Warning: Vendor user not found! Trying to fetch any user...")
        vendor = User.objects.filter(is_staff=False).first()
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

    print(f"\n🎉 === SEED COMPLETE ===")
    print(f"   Total Users: {User.objects.count()}")
    print(f"   Total Products: {Product.objects.count()}")
    print(f"   New Products Added: {count}")
    print("   Login with: customer@public.com / PublicPass123!")
    print("========================\n")

if __name__ == "__main__":
    print("🚀 Script started...")
    try:
        seed_data()
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()