from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations

from decimal import Decimal

from ftw.shop.interfaces import IVariationConfig
from ftw.shop.interfaces.shopitem import IShopItem

from persistent.mapping import PersistentMapping
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


class VariationConfig(object):
    """An Adapter for storing variation configurations on ShopItems
    """
    
    implements(IVariationConfig)
    adapts(IShopItem)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)
        
    def hasVariations(self):
        return self.context.Schema().getField('variation1_attribute').get(self.context) not in (None, '')
        

    def getVariationConfig(self):
        return self.annotations.get('variations', PersistentMapping())

    def updateVariationConfig(self, data):
        if not 'variations' in self.annotations.keys():
            self.annotations['variations'] = PersistentMapping()
        self.annotations['variations'].update(data)

    def getVariation1Values(self):
        value_string = getattr(self.context, 'variation1_values', None)
        if value_string:
            return [v.strip() for v in value_string.split(',')]
        else:
            return []


    def getVariation2Values(self):
        value_string = getattr(self.context, 'variation2_values', None)
        if value_string:
            return [v.strip() for v in value_string.split(',')]
        else:
            return []


    def getVariationData(self, var1_attr, var2_attr, field):
        variation_data= self.getVariationConfig()
        normalizer = getUtility(IIDNormalizer)
        
        variation_key = normalizer.normalize("%s-%s" % (var1_attr, var2_attr))
        var_dict = variation_data.get(variation_key, None)
        if var_dict is not None and field in var_dict.keys():
            if not var_dict[field] == "":
                return var_dict[field]
        # Return a default value appropriate for the field type
        if field == 'active':
            return True
        elif field == 'price':
            return Decimal("%s.%02d" % self.context.price)
        elif field == 'stock':
            return 0
        elif field == 'skuCode':
            return ""
        else:
            return None
