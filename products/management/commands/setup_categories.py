from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Reset and seed ONLY the correct category tree'

    DATA = {
        'Electronics': [
            'Laptops', 
            'SmartPhones', 
            'Accessories',
            'Home Appliances'
        ],
        'Fashion': [
            "Men's Clothing", 
            "Women's Clothing", 
            'Shoes',  
            'Bags & Watches'
        ],
        'Home & Living': [
            'Furniture', 
            'Kitchenware', 
            'Decor', 
        ],
        'Food & Groceries': [
            'Beverages',
            'Grains & Rice',
            'Fruits',
            'Snacks'
        ]
    }

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️ Deleting ALL categories...'))

        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✔ Database cleaned'))

        for parent_name, children in self.DATA.items():
            parent = Category.objects.create(
                name=parent_name,
                parent=None
            )
            self.stdout.write(self.style.SUCCESS(f'[+] {parent_name}'))

            for child_name in children:
                Category.objects.create(
                    name=child_name,
                    parent=parent
                )
                self.stdout.write(f'   └─ {child_name}')

        self.stdout.write(self.style.SUCCESS('✅ Categories seeded successfully'))
