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

CATEGORY_RELATIONSHIP = 'shop_category'
