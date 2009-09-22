"""Definition of the Shop Category content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from amnesty.base.content.aiarticle import AIArticle
from amnesty.base.content.aiarticle import AIArticleSchema
from amnesty.shop import shopMessageFactory as _
from amnesty.shop.interfaces import IShopCategory
from amnesty.shop.config import PROJECTNAME
from amnesty.shop.content.categorizeable import Categorizeable

class ShopCategory(Categorizeable, AIArticle):
    """A category for shop items"""
    implements(IShopCategory)

    meta_type = "ShopCategory"
    schema = AIArticleSchema.copy()

atapi.registerType(ShopCategory, PROJECTNAME)
