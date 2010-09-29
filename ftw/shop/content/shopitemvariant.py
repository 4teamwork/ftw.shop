"""Definition of the Shop Item Variant content type
"""

from zope.interface import implements, alsoProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content import schemata
from DateTime import DateTime
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces.shopitemvariant import IShopItemVariant
from ftw.shop.config import PROJECTNAME
from ftw.shop.content.shopitem import ShopItemSchema

from ftw.shop.interfaces import IShoppable


ShopItemVariantSchema = ShopItemSchema.copy() #+ atapi.Schema((
                                  
#     atapi.StringField('variantLabel',
#         searchable = 0,
#         required = 0,
#         widget = atapi.StringWidget(
#             label = _(u"label_variant_label", default=u"Variant Label"),
#             description = _(u"desc_variant_label", default=u"e.g. Color. All variant items with the same label will be grouped together."),
#         ),        
#     ),
#     
# ),)

schemata.finalizeATCTSchema(ShopItemVariantSchema, moveDiscussion=False)
# ShopItemVariantSchema.moveField('price', after='variantLabel')
# ShopItemVariantSchema.moveField('sku_code', after='variantLabel')
# ShopItemVariantSchema.moveField('currency', after='price')
# ShopItemVariantSchema['description'].widget.visible = {'edit' : 'invisible', 'view' : 'invisible' }
# ShopItemVariantSchema['subject'].widget.visible = {'edit' : 'invisible', 'view' : 'invisible' }
# ShopItemVariantSchema['location'].widget.visible = {'edit' : 'invisible', 'view' : 'invisible' }
# ShopItemVariantSchema['relatedItems'].widget.visible = {'edit' : 'invisible', 'view' : 'invisible' }
# ShopItemVariantSchema['effectiveDate'].default = DateTime()

class ShopItemVariant(ATFolder):
    """A shop item variant for multi items"""
    implements(IShopItemVariant)
    alsoProvides(IShoppable)

    meta_type = "ShopItemVariant"
    schema = ShopItemVariantSchema

atapi.registerType(ShopItemVariant, PROJECTNAME)
