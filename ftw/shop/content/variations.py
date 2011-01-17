from decimal import Decimal
from decimal import InvalidOperation

from persistent.mapping import PersistentMapping
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.component import adapts, getUtility

from ftw.shop.interfaces import IVariationConfig, IShopItem


class VariationConfig(object):
    """An Adapter for storing variation configurations on ShopItems
    """

    implements(IVariationConfig)
    adapts(IShopItem)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def hasVariations(self):
        """Determines if the item has variations or not
        """
        field = self.context.Schema().getField('variation1_attribute')
        return field.get(self.context) not in (None, '')

    def getItemUID(self):
        """Returns the ShopItem's UID
        """
        return self.context.UID()

    def getVariationDict(self):
        """Returns a nested dict with the variation config for the item
        """
        return self.annotations.get('variations', PersistentMapping())

    def updateVariationConfig(self, data):
        """Updates the stored variation config with changes
        """
        if not 'variations' in self.annotations.keys():
            self.annotations['variations'] = PersistentMapping()
        self.annotations['variations'].update(data)

    def getVariation1Values(self):
        """Returns the values for the top level variation,
        e.g. ['Red', 'Green', 'Blue']
        """
        values = self.context.getField('variation1_values').get(self.context)
        if values:
            return values
        else:
            return []

    def getVariation2Values(self):
        """Returns the values for the second level variation,
        e.g. ['S', 'M', 'L', 'XL']
        """
        values = self.context.getField('variation2_values').get(self.context)
        if values:
            return values
        else:
            return []

    def getVariationAttributes(self):
        """Returns a list of the two variation attributes,
        e.g. ['Color', 'Size']
        """
        variation_attributes = []
        for name in ['variation1_attribute', 'variation2_attribute']:
            field = self.context.Schema().getField(name)
            if field.get(self.context) not in (None, ''):
                variation_attributes.append(field.get(self.context))
        return variation_attributes

    def getVariationData(self, var1_idx, var2_idx, field):
        """Returns the data for one specific variation instance's field
        """
        variation_dict = self.getVariationDict()

        if var2_idx is None:
            # We only have one variation
            variation_code = "var-%s" % var1_idx
        else:
            # We have two levels of variation
            variation_code = "var-%s-%s" % (var1_idx, var2_idx)
        var_data = variation_dict.get(variation_code, None)
        if var_data is not None and field in var_data.keys():
            if not var_data[field] == "":
                return var_data[field]

        # Return a default value appropriate for the field type
        if field == 'active':
            return True
        elif field == 'price':
            return Decimal("%s.%02d" % self.context.price)
        elif field == 'skuCode':
            return self.context.skuCode
        elif field == 'description':
            return ''
        elif field == 'hasUniqueSKU':
            return False
        else:
            return None

    def getPrettyName(self, variation_code):
        """Returns the human facing name for a variation,
        e.g. 'Green-XXL'
        """
        if len(self.getVariationAttributes()) == 1:
            for i, var1_value in enumerate(self.getVariation1Values()):
                vcode = "var-%s" % i
                if vcode == variation_code:
                    return var1_value
        else:
            for i, var1_value in enumerate(self.getVariation1Values()):
                for j, var2_value in enumerate(self.getVariation2Values()):
                    vcode = "var-%s-%s" % (i, j)
                    if vcode == variation_code:
                        return "%s-%s" % (var1_value, var2_value)
        return None


    def isValid(self):
        var_dict = self.getVariationDict()
        variation_states = []

        for key in var_dict:
            variation_states.append(var_dict[key].get('hasUniqueSKU', False))
        if False in variation_states or variation_states == []:
            return False
        else:
            return True

    def allPricesZero(self):
        var_dict = self.getVariationDict()
        try:
            prices = [Decimal(var_dict[k].get('price', '0.0'))
                            for k in var_dict]
            return all([p == Decimal('0.0') for p in prices])
        except InvalidOperation:
            return False

    