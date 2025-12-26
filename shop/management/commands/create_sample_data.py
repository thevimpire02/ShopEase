from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductImage
from decimal import Decimal
import os

class Command(BaseCommand):
    help = 'Creates sample categories and products for the ecommerce site'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Categories
        categories_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Latest electronic devices and gadgets'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashionable clothing for all occasions'},
            {'name': 'Books', 'slug': 'books', 'description': 'Books for all reading preferences'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Everything for your home and garden'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Create Products
        products_data = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'High-quality wireless headphones with noise cancellation and 30-hour battery life.',
                'price': Decimal('79.99'),
                'discount_price': Decimal('59.99'),
                'category': 'electronics',
                'brand': 'TechSound',
                'stock': 50
            },
            {
                'name': 'Smartphone 128GB',
                'slug': 'smartphone-128gb',
                'description': 'Latest smartphone with 128GB storage, 6.5" display, and triple camera system.',
                'price': Decimal('599.99'),
                'discount_price': None,
                'category': 'electronics',
                'brand': 'TechPhone',
                'stock': 25
            },
            {
                'name': 'Cotton T-Shirt',
                'slug': 'cotton-tshirt',
                'description': 'Comfortable 100% cotton t-shirt available in multiple colors and sizes.',
                'price': Decimal('19.99'),
                'discount_price': Decimal('14.99'),
                'category': 'clothing',
                'brand': 'FashionWear',
                'stock': 100
            },
            {
                'name': 'Denim Jeans',
                'slug': 'denim-jeans',
                'description': 'Classic fit denim jeans with stretch for comfort. Available in various sizes.',
                'price': Decimal('49.99'),
                'discount_price': None,
                'category': 'clothing',
                'brand': 'FashionWear',
                'stock': 75
            },
            {
                'name': 'Python Programming Book',
                'slug': 'python-programming-book',
                'description': 'Comprehensive guide to Python programming for beginners and intermediate developers.',
                'price': Decimal('39.99'),
                'discount_price': Decimal('29.99'),
                'category': 'books',
                'brand': 'TechBooks',
                'stock': 30
            },
            {
                'name': 'Web Development Guide',
                'slug': 'web-development-guide',
                'description': 'Complete guide to modern web development with HTML, CSS, and JavaScript.',
                'price': Decimal('44.99'),
                'discount_price': None,
                'category': 'books',
                'brand': 'TechBooks',
                'stock': 20
            },
            {
                'name': 'Coffee Maker',
                'slug': 'coffee-maker',
                'description': 'Programmable coffee maker with 12-cup capacity and auto-shutoff feature.',
                'price': Decimal('89.99'),
                'discount_price': Decimal('69.99'),
                'category': 'home-garden',
                'brand': 'HomeEssentials',
                'stock': 40
            },
            {
                'name': 'Garden Tool Set',
                'slug': 'garden-tool-set',
                'description': 'Complete garden tool set including shovel, rake, pruners, and gloves.',
                'price': Decimal('59.99'),
                'discount_price': None,
                'category': 'home-garden',
                'brand': 'GardenPro',
                'stock': 15
            },
            {
                'name': 'Laptop Stand',
                'slug': 'laptop-stand',
                'description': 'Ergonomic aluminum laptop stand with adjustable height and ventilation.',
                'price': Decimal('34.99'),
                'discount_price': Decimal('24.99'),
                'category': 'electronics',
                'brand': 'TechAccessories',
                'stock': 60
            },
            {
                'name': 'Winter Jacket',
                'slug': 'winter-jacket',
                'description': 'Warm and waterproof winter jacket with insulated lining. Perfect for cold weather.',
                'price': Decimal('129.99'),
                'discount_price': Decimal('99.99'),
                'category': 'clothing',
                'brand': 'OutdoorGear',
                'stock': 35
            },
        ]
        
        created_count = 0
        for prod_data in products_data:
            category = categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'discount_price': prod_data['discount_price'],
                    'category': category,
                    'brand': prod_data['brand'],
                    'stock': prod_data['stock'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n[SUCCESS] Sample data created successfully!\n'
            f'   - Categories: {len(categories)}\n'
            f'   - Products: {created_count} new products created\n'
            f'\nYou can now access the site at http://127.0.0.1:8000/'
        ))

