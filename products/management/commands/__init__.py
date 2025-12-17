from django.core.management.base import BaseCommand
from products.models import Category
from django.utils.text import slugify
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Safely populates the database with your specific Category Tree'

    def handle(self, *args, **kwargs):
        # YOUR SPECIFIC DATA STRUCTURE
        DATA = {
            'Electronics': [
                'Laptops', 
                'SmartPhones', 
                'Accessories',
                'Home Appliances'
            ],
            'Fashion': [
                'Men\'s Clothing', 
                'Women\'s Clothing', 
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

        self.stdout.write('Starting Category Seeding...')

        # Loop through the Dictionary
        for parent_name, subcats in DATA.items():
            
            # 1. Create (or get) the Parent
            # We assume 'parent=None' for top-level categories
            parent_obj, created = Category.objects.get_or_create(
                name=parent_name, 
                defaults={'parent': None}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'[+] Created Parent: {parent_name}'))
            else:
                self.stdout.write(f'[-] Exists: {parent_name}')

            # 2. Create the Children
            for sub_name in subcats:
                sub_obj, sub_created = Category.objects.get_or_create(
                    name=sub_name, 
                    defaults={'parent': parent_obj} # LINK TO PARENT
                )
                
                if sub_created:
                    self.stdout.write(self.style.SUCCESS(f'   -> Created Sub: {sub_name}'))

        self.stdout.write(self.style.SUCCESS('----------------------------------'))
        self.stdout.write(self.style.SUCCESS('SUCCESS: Category Tree Populated!'))