"""Definition of the Shop Category content type
"""

from zope.interface import implements
from Products.Archetypes import atapi
# from amnesty.base.content.aiarticle import AIArticle
# from amnesty.base.content.aiarticle import AIArticleSchema
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from ftw.shop.interfaces.shopcategory import IShopCategory
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.categorizeable import Categorizeable


class ShopCategory(Categorizeable, ATDocument):
    """A category for shop items"""
    implements(IShopCategory)

    meta_type = "ShopCategory"
    schema = ATDocumentSchema.copy()

atapi.registerType(ShopCategory, PROJECTNAME)
