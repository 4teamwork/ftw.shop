from decimal import Decimal
from decimal import InvalidOperation
from ftw.shop.interfaces import IVariationConfig, IShopItem
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements
import itertools


try:
    dummy = type(all)
except NameError:
    # Python 2.4
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True


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

    def key(self, varcode1=None, varcode2=None):
        """A unique id for each item and variation combination.
        """
        if varcode1 is None:
            return self.context.UID()
        if varcode2 is None:
            return '%s-%s' % (self.context.UID(), varcode1)
        return '%s-%s-%s' % (self.context.UID(), varcode1, varcode2)

    def variation_code(self, var1choice=None, var2choice=None):
        """
        """
        if var1choice is None:
            return ''
        if var2choice is None:
            return 'var-%s' % var1choice
        return 'var-%s-%s' % (var1choice, var2choice)

    def sku_code(self, var1choice=None, var2choice=None):
        """Returns the sku code for the given variation combination.
        """
        vcode = self.variation_code(var1choice, var2choice)
        if not vcode:
            return self.context.getField('skuCode').get(self.context)
        return self.getVariationDict().get(vcode).get('skuCode')


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
        # Since skuCode uniqueness isn't required any more,
        # variation configs are always assumed to be valid
        return True


    def allPricesZero(self):
        var_dict = self.getVariationDict()
        try:
            prices = [Decimal(var_dict[k].get('price', '0.0'))
                            for k in var_dict]
            return all([p == Decimal('0.0') for p in prices])
        except InvalidOperation:
            return False

    def purge_dict(self):
        self.annotations['variations'] = PersistentMapping()

    def reduce_level(self):
        if len(self.getVariationAttributes()) == 2:
            # Reduce from 2 to 1 variation
            var_dict = self.getVariationDict()
            new_var_dict = PersistentMapping()
            vcodes = sorted(var_dict.keys())
            for i, vcode in enumerate(vcodes):
                new_vcode = 'var-%s' % i
                new_var_dict[new_vcode] = var_dict[vcode]

            self.annotations['variations'] = new_var_dict
            new_values = []

            combinations = itertools.product(self.getVariation1Values(), self.getVariation2Values())
            for pair in combinations:
                val = '-'.join(pair)
                new_values.append(val)

            new_attr = "%s/%s" % (self.getVariationAttributes()[0],
                                  self.getVariationAttributes()[1])

            self.context.getField('variation2_values').set(self.context, [])
            self.context.getField('variation2_attribute').set(self.context, None)

            self.context.getField('variation1_values').set(self.context, new_values)
            self.context.getField('variation1_attribute').set(self.context, new_attr)

        elif len(self.getVariationAttributes()) == 1:
            # Reduce from 1 to 0 variations
            self.context.getField('variation1_values').set(self.context, [])
            self.context.getField('variation1_attribute').set(self.context, None)

            self.context.getField('variation2_values').set(self.context, [])
            self.context.getField('variation2_attribute').set(self.context, None)

            self.annotations['variations'] = PersistentMapping()


    def remove_level(self):
        if len(self.getVariationAttributes()) == 2:
            self.context.getField('variation2_values').set(self.context, [])
            self.context.getField('variation2_attribute').set(self.context, None)
            self.purge_dict()
        elif len(self.getVariationAttributes()) == 1:
            self.context.getField('variation1_values').set(self.context, [])
            self.context.getField('variation1_attribute').set(self.context, None)
            self.context.getField('variation2_values').set(self.context, [])
            self.context.getField('variation2_attribute').set(self.context, None)
            self.purge_dict()


    def add_level(self):
        fields = ['active', 'skuCode', 'price', 'description']
        if len(self.getVariationAttributes()) == 1:
            self.context.getField('variation2_values').set(self.context, ['Neuer Wert 1', 'Neuer Wert2'])
            self.context.getField('variation2_attribute').set(self.context, 'Neues Attribut')

            # Initialize var data for newly added level with default values
            for i in range(len(self.getVariation1Values())):
                for j in range(len(self.getVariation2Values())):
                    vardata = {}
                    for f in fields:
                        vcode = "var-%s-%s" % (i, j)
                        data = self.getVariationData(i, j, f)
                        vardata[f] = data
                        partial_vardict = {vcode: vardata}
                        self.updateVariationConfig(partial_vardict)

        elif len(self.getVariationAttributes()) == 0:
            self.context.getField('variation1_values').set(self.context, ['Neuer Wert 1', 'Neuer Wert2'])
            self.context.getField('variation1_attribute').set(self.context, 'Neues Attribut')

            # Initialize var data for newly added level with default values
            for i in range(len(self.getVariation1Values())):
                vardata = {}
                for f in fields:
                    vcode = "var-%s" % (i)
                    data = self.getVariationData(i, None, f)
                    vardata[f] = data
                    partial_vardict = {vcode: vardata}
                    self.updateVariationConfig(partial_vardict)
