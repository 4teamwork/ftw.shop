"""Common configuration constants
"""
from Products.Archetypes.public import DisplayList
from decimal import Decimal

PROJECTNAME = 'ftw.shop'

ADD_PERMISSIONS = {
    'ShopCategory': 'ftw.shop: Add Shop Category',
    'ShopItem': 'ftw.shop: Add Shop Item',
    'Supplier': 'ftw.shop: Add Supplier',
}

CURRENCIES = DisplayList((
    ('CHF', 'CHF'), # CHF
#      ('USD', 'US$'), # U.S. Dollars
#      ('EUR', 'Eur'), # Euros
))

SESSION_ORDERS_KEY = 'ftw.shop.orders'
SESSION_ADDRESS_KEY = 'ftw.shop.customer_data'
SESSION_SHIPPING_KEY = 'ftw.shop.shipping_address'
SESSION_REVIEW_KEY = 'ftw.shop.review_data'
SESSION_ERRORS_KEY = 'ftw.shop.errors'

COOKIE_ADDRESS_KEY = 'ftw.shop.customer_cookie'

ONLINE_PENDING_KEY = 1
ONLINE_CONFIRMED_KEY = 2
ONACCOUNT_KEY = 3

CART_KEY = 'shop_cart_items'

CATEGORY_RELATIONSHIP = 'shop_category'

DEFAULT_VAT_RATES = [Decimal('0.0'), Decimal('8.0'), Decimal('2.5')]
