import os
import django
import random
from faker import Faker

# --------------------
# Django setup
# --------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

fake = Faker()

# --------------------
# Clear existing data (optional)
# --------------------
print("Clearing existing data...")
Order.objects.all().delete()
Product.objects.all().delete()
Customer.objects.all().delete()

# --------------------
# Seed Customers
# --------------------
print("Creating customers...")
customers = []
for _ in range(10):
    customer = Customer.objects.create(
        name=fake.name(),
        email=fake.unique.email(),
        phone=fake.phone_number() if random.choice([True, False]) else None
    )
    customers.append(customer)

# --------------------
# Seed Products
# --------------------
print("Creating products...")
products = []
for _ in range(10):
    product = Product.objects.create(
        name=fake.word().capitalize(),
        price=round(random.uniform(10, 1000), 2),
        stock=random.randint(0, 50)
    )
    products.append(product)

# --------------------
# Seed Orders
# --------------------
print("Creating orders...")
for _ in range(15):
    customer = random.choice(customers)
    selected_products = random.sample(products, random.randint(1, 3))
    order = Order.objects.create(customer=customer)
    order.products.set(selected_products)
    order.total_amount = sum(p.price for p in selected_products)
    order.save()

print("Seeding completed successfully!")
