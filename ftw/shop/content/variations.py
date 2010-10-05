from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from ftw.shop.interfaces import IVariationConfig
from ftw.shop.interfaces.shopitem import IShopItem

from persistent.mapping import PersistentMapping

class VariationConfig(object):
    """An Adapter for storing variation configurations on ShopItems
    """
    
    implements(IVariationConfig)
    adapts(IShopItem)
    
    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        
    def getVariationConfig(self):
        return self.annotations.get('variations', PersistentMapping())

    def updateVariationConfig(self, data):
        if not 'variations' in self.annotations.keys():
            self.annotations['variations'] = PersistentMapping()
        self.annotations['variations'].update(data)
