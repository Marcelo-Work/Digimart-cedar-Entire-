#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Profile, Product, Order, OrderItem, Cart

User = get_user_model()


def seed_private_data():
    """Create private test user and data for Task 2 evaluation."""
    
    print("="*60)
    print("Task 2: Seeding Private Test Data")
    print("="*60)
    private_email = 'customer@private.com'
    private_password = 'PrivatePass123!'
    private_username = 'customer_private'
    
    print(f"\nCreating private user: {private_email}")
    
    existing_user = User.objects.filter(email=private_email).first()
    if existing_user:
        print(f"  - Deleting existing user: {existing_user.username}")
        existing_user.delete()
    
    # Create new private user
    private_user = User.objects.create_user(
        username=private_username,
        email=private_email,
        password=private_password
    )
    print(f"  ✅ Created user: {private_user.username} (ID: {private_user.id})")
    
    print(f"\nCreating Profile for {private_username}")
    
    profile, created = Profile.objects.get_or_create(
        user=private_user,
        defaults={
            'role': 'customer',
        }
    )
    if created:
        print(f"  ✅ Created new Profile")
    else:
        print(f"  ✅ Profile already exists")
    
    print(f"\nSeeding private products...")
    
    private_products = [
        {
            'title': 'Private Digital Asset Alpha',
            'description': 'Exclusive private product for testing avatar upload and order flow.',
            'price': '29.99',
            'file_url': 'https://example.com/private-alpha.zip',
        },
        {
            'title': 'Private Digital Asset Beta',
            'description': 'Another private product for comprehensive testing.',
            'price': '49.99',
            'file_url': 'https://example.com/private-beta.zip',
        },
    ]
    
    for prod_data in private_products:
        product, created = Product.objects.get_or_create(
            title=prod_data['title'],
            defaults={
                'description': prod_data['description'],
                'price': prod_data['price'],
                'file_url': prod_data['file_url'],
                'vendor': private_user,
            }
        )
        status = "Created" if created else "Exists"
        print(f"  - {prod_data['title']}: {status}")
    
    print(f"\nSeeding private cart...")
    
    cart, created = Cart.objects.get_or_create(
        user=private_user,
        defaults={'items': []}
    )
    print(f"  ✅ Cart ready for {private_username}")
    

    print("\n" + "="*60)
    print("Private Seed Complete!")
    print("="*60)
    print(f"User:    {private_email}")
    print(f"Password: {private_password}")
    print(f"Profile: {profile.role}")
    print(f"Products: {Product.objects.filter(vendor=private_user).count()}")
    print("\n✅ Ready for Task 2 Private Evaluation Tests")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        seed_private_data()
        print("✅ Seed script completed successfully")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Seed script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)