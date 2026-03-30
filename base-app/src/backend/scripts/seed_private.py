import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from api.models import User, Product, Order, OrderItem
from django.db import transaction

@transaction.atomic
def seed_private_data():
    print("🌱 Starting PRIVATE data seeding...")

    users_data = [
        {
            "username": "admin_private",
            "email": "admin@private.com",
            "password": "PrivateAdminPass99!",
            "role": "admin",
            "is_staff": True,
            "is_superuser": True
        },
        {
            "username": "vendor_private",
            "email": "vendor@private.com",
            "password": "PrivateVendorPass99!",
            "role": "vendor",
            "is_staff": False,
            "is_superuser": False
        },
        {
            "username": "customer_private",
            "email": "customer@private.com",
            "password": "PrivateCustomerPass99!",
            "role": "customer",
            "is_staff": False,
            "is_superuser": False
        }
    ]

    created_users = {}

    for u_data in users_data:
        user, created = User.objects.get_or_create(username=u_data["username"])

        user.set_password(u_data["password"])
        user.email = u_data["email"]
        user.is_staff = u_data["is_staff"]
        user.is_superuser = u_data["is_superuser"]
        
        if hasattr(user, 'role'):
            user.role = u_data["role"]
        
        user.save()
        
        status = "Created" if created else "Updated"
        print(f"   ✅ {status} User: {u_data['username']} ({u_data['role']})")
        created_users[u_data["role"]] = user


    vendor_user = created_users.get("vendor")
    if not vendor_user:
        print("   ❌ ERROR: Vendor user not found! Cannot create products.")
        return

    products_data = [
        {"title": "Private Gaming Mouse", "price": "59.99", "desc": "High DPI mouse for private testing."},
        {"title": "Secret Strategy Ebook", "price": "19.99", "desc": "Exclusive guide for private users."},
        {"title": "Private Cloud Storage Key", "price": "99.00", "desc": "1TB encrypted storage access key."},
        {"title": "Exclusive Beta Access Token", "price": "150.00", "desc": "Early access token for private testers."},
        {"title": "Private Developer License", "price": "299.99", "desc": "Annual license for private dev tools."},
        {"title": "Confidential Data Set", "price": "49.50", "desc": "Anonymized dataset for private analysis."},
        {"title": "Private API Gateway Key", "price": "75.00", "desc": "Unlimited API access key for private use."},
        {"title": "Stealth Mode Plugin", "price": "29.99", "desc": "Browser plugin for private browsing enhancement."},
        {"title": "Private Server Config", "price": "120.00", "desc": "Optimized configuration files for private servers."},
        {"title": "Encrypted Chat Module", "price": "85.00", "desc": "End-to-end encryption module for private comms."}
    ]

    print("\n   📦 Creating Private Products...")
    count = 0
    for p_data in products_data:
        obj, created = Product.objects.get_or_create(
            title=p_data["title"],
            defaults={
                "price": p_data["price"],
                "description": p_data["desc"],
                "vendor": vendor_user,
                "file_url": f"https://via.placeholder.com/300?text={p_data['title'].replace(' ', '+')}"
            }
        )
        if created:
            count += 1
            print(f"      ➕ Created: {p_data['title']}")
        else:
            print(f"      ⏭️  Exists: {p_data['title']}")

  
    customer_user = created_users.get("customer")
    if customer_user and vendor_user:
        print("\n   🛒 Creating Private Sample Orders...")
        all_products = list(Product.objects.filter(vendor=vendor_user)[:3])
        if all_products:
            order, created = Order.objects.get_or_create(
                user=customer_user,
                status="completed",
                defaults={"total_amount": sum(float(p.price) for p in all_products)}
            )
            if created:
                for prod in all_products:
                    OrderItem.objects.get_or_create(
                        order=order,
                        product=prod,
                        defaults={"quantity": 1, "license_key": f"PRIVATE-KEY-{prod.id}-XYZ"}
                    )
                print(f"      ➕ Created Order #{order.id} for {customer_user.username}")
            else:
                print(f"      ⏭️  Order exists for {customer_user.username}")

    print(f"\n🎉 === PRIVATE SEED COMPLETE ===")
    print(f"   Total Users: {User.objects.count()}")
    print(f"   Total Products: {Product.objects.count()}")
    print(f"   New Private Products Added: {count}")
    print(f"   Login with: customer@private.com / PrivateCustomerPass99!")
    print("===============================\n")

if __name__ == "__main__":
    try:
        seed_private_data()
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)