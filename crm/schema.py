import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from crm.models import Customer, Product, Order
from crm.filters import CustomerFilter, ProductFilter, OrderFilter
from datetime import datetime
import re

# --------------------
# Object Types
# --------------------
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

# --------------------
# Mutations
# --------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerNode)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise GraphQLError("Email already exists")
        if input.phone and not re.match(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$', input.phone):
            raise GraphQLError("Invalid phone format")
        customer = Customer.objects.create(**input)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerNode)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, inputs):
        created, errors = [], []
        for idx, input in enumerate(inputs):
            try:
                result = CreateCustomer.mutate(root, info, input)
                created.append(result.customer)
            except GraphQLError as e:
                errors.append(f"Customer {idx+1}: {str(e)}")
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductNode)

    @staticmethod
    def mutate(root, info, name, price, stock):
        if price <= 0: raise GraphQLError("Price must be positive")
        if stock < 0: raise GraphQLError("Stock cannot be negative")
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderNode)

    @staticmethod
    def mutate(root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")
        products = Product.objects.filter(id__in=product_ids)
        if len(products) != len(product_ids):
            raise GraphQLError("One or more product IDs are invalid")
        order_date = order_date or datetime.now()
        order = Order.objects.create(customer=customer, order_date=order_date)
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()
        return CreateOrder(order=order)

# --------------------
# Root Mutation
# --------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# --------------------
# Root Query with Filtering
# --------------------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    all_orders = DjangoFilterConnectionField(OrderNode)
import graphene
from crm.models import Product
from graphene_django.types import DjangoObjectType

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no args needed

    success = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10  # simulate restocking
            product.save()
            updated.append(product)

        return
