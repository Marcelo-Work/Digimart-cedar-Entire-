from api.models import User, Product, Cart

customer = User.objects.create_user(
    email='customer@private.com',
    username='customer_private',
    password='PrivatePass456!',
    first_name='Alice',
    last_name='Johnson',
    role='customer'
)

vendor = User.objects.create_user(
    email='vendor@private.com',
    username='vendor_private',
    password='PrivatePass456!',
    first_name='Bob',
    last_name='Williams',
    role='vendor'
)

admin = User.objects.create_user(
    email='admin@private.com',
    username='admin_private',
    password='PrivatePass456!',
    first_name='Admin',
    last_name='Private',
    role='admin'
)

products_data = [
    {'title': 'Premium Ebook X-99', 'price': '34.99', 'description': 'Exclusive content'},
    {'title': 'Pro Software Suite', 'price': '149.99', 'description': 'Professional tools'},
    {'title': 'Digital Art Pack', 'price': '59.99', 'description': 'Artist resources'},
    {'title': 'Music Production Kit', 'price': '89.99', 'description': 'Audio tools'},
    {'title': 'Video Course Bundle', 'price': '199.99', 'description': 'Learning content'},
    {'title': 'Template Collection', 'price': '44.99', 'description': 'Ready templates'},
    {'title': 'Plugin Library', 'price': '79.99', 'description': 'Developer tools'},
    {'title': 'Stock Media Pack', 'price': '54.99', 'description': 'Media assets'},
    {'title': 'Font Studio', 'price': '39.99', 'description': 'Typography'},
    {'title': 'Icon Pro Set', 'price': '29.99', 'description': 'UI elements'},
]

for prod in products_data:
    Product.objects.create(
        title=prod['title'],
        description=prod['description'],
        price=prod['price'],
        file_url=f'/downloads/{prod["title"].lower().replace(" ", "-")}',
        vendor=vendor
    )

Cart.objects.create(user=customer, items=[])

print("✅ Private seed completed!")