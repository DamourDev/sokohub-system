from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # save an empty cart in the session
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product):
        """
        Add a product to the cart or increment its quantity.
        Used by: 'Add to Cart' button AND '(+)' Icon.
        """
        product_id = str(product.id)
        
        # If product is not in cart, create it
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        
        # Always just add +1
        self.cart[product_id]['quantity'] += 1
        
        self.save()

    def decrement(self, product):
        """
        Decrease the quantity of a product by 1.
        Used by: '(-)' Icon.
        Logic: Stops at 1 (does not auto-delete).
        """
        product_id = str(product.id)
        
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] > 1:
                self.cart[product_id]['quantity'] -= 1
                self.save()

    def remove(self, product):
        """
        Remove a product from the cart completely.
        Used by: Trash Icon.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        # Mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def __iter__(self):
       
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def get_total_price(self):
        """
        Calculate the total cost of all items in the cart.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())