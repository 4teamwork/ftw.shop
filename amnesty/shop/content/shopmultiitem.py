"""Definition of the Shop Multi Item content type
"""

from zope.interface import implements

from Products.Archetypes import atapi

from amnesty.base.content.aiarticle import AIArticle
from amnesty.base.content.aiarticle import AIArticleSchema
from amnesty.shop import shopMessageFactory as _
from amnesty.shop.interfaces import IShopMultiItem
from amnesty.shop.content.categorizeable import Categorizeable
from amnesty.shop.config import PROJECTNAME

ShopMultiItemSchema = AIArticleSchema.copy() 

class ShopMultiItem(Categorizeable, AIArticle):
    """A shop item that consists of multiple variants (eg. colors, sizes)"""
    implements(IShopMultiItem)

    meta_type = "ShopMultiItem"
    schema = ShopMultiItemSchema

atapi.registerType(ShopMultiItem, PROJECTNAME)
