"""Definition of the Shop Item content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from amnesty.base.content.aiarticle import AIArticle
from amnesty.base.content.aiarticle import AIArticleSchema
from amnesty.shop import shopMessageFactory as _
from amnesty.shop.interfaces import IShopItem
from amnesty.shop.content.categorizeable import Categorizeable
from amnesty.shop.config import PROJECTNAME, CURRENCIES

ShopItemBaseSchema = atapi.Schema((

    atapi.StringField('currency',
        required = 1,
        vocabulary = CURRENCIES,
        default = CURRENCIES[0],
        widget = atapi.SelectionWidget(
            label = _(u"label_currency", default=u"Currency"),
            description = _(u"desc_currency", default=u""),
        ),
    ),
    
    atapi.FixedPointField('price',
        default = "0.00",
        required = 0,
        accessor = "Price",
        widget = atapi.DecimalWidget(
            label = _(u"label_price", default=u"Price"),
            description = _(u"desc_price", default=u""),
            size=8,
        ),
    ),
    
    atapi.StringField('sku_code',
        required = 1,
        widget = atapi.StringWidget(
            label = _(u"label_sku_code", default=u"SKU Code"),
            description = _(u"desc_sku_code", default=u""),
        ),
    ),
    
),)

ShopItemSchema = AIArticleSchema.copy() + ShopItemBaseSchema
ShopItemSchema.moveField('price', after='realTitle')
ShopItemSchema.moveField('sku_code', after='realTitle')

class ShopItem(Categorizeable, AIArticle):
    """A simple shop item"""
    implements(IShopItem)

    meta_type = "ShopItem"
    schema = ShopItemSchema

atapi.registerType(ShopItem, PROJECTNAME)
