"""Common configuration constants
"""
from Products.Archetypes.public import DisplayList

PROJECTNAME = 'amnesty.shop'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'ShopCategory': 'amnesty.shop: Add Shop Category',
    'ShopItemVariant': 'amnesty.shop: Add Shop Item Variant',
    'ShopMultiItem': 'amnesty.shop: Add Shop Multi Item',
    'ShopItem': 'amnesty.shop: Add Shop Item',
}

CURRENCIES = DisplayList((
    ('CHF', 'CHF'), # CHF                            
#      ('USD', 'US$'), # U.S. Dollars
#      ('EUR', 'Eur'), # Euros
))

CATEGORY_RELATIONSHIP = 'shop_category'
