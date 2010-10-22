"""Common configuration constants
"""
from Products.Archetypes.public import DisplayList

PROJECTNAME = 'ftw.shop'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'ShopCategory': 'ftw.shop: Add Shop Category',
    'ShopItem': 'ftw.shop: Add Shop Item',
    'ShopOrder': 'ftw.shop: Add Order',
}

CURRENCIES = DisplayList((
    ('CHF', 'CHF'), # CHF                            
#      ('USD', 'US$'), # U.S. Dollars
#      ('EUR', 'Eur'), # Euros
))

SESSION_ORDERS_KEY = 'ftw.shop.orders'
SESSION_ADDRESS_KEY = 'ftw.shop.customer_data'
SESSION_ERRORS_KEY = 'ftw.shop.errors'

ONLINE_PENDING_KEY = 1
ONLINE_CONFIRMED_KEY = 2
ONACCOUNT_KEY = 3 


CATEGORY_RELATIONSHIP = 'shop_category'
