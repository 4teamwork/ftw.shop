from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from zope.interface import Interface, implements
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IVariationConfig
from decimal import Decimal

     
class ShopItemView(BrowserView):
    """Default view for a shop item
    """
    
    __call__ = ViewPageTemplateFile('shopitem.pt')
    
    @property
    @instance.memoize    
    def item(self):
        context = aq_inner(self.context)
        if context.portal_type == 'ShopItem':
            return dict(
                order_number = context.Schema().getField('skuCode').get(context),
                price = context.Schema().getField('price').get(context),
                url = '%s/addtocart' % context.absolute_url(),
            )
        return None

    @property
    @instance.memoize
    def items(self):
        context = aq_inner(self.context)
        if context.portal_type == 'ShopItem':
            ct = getToolByName(context, 'portal_catalog')
            query = {}
            query['path'] = {'query': '/'.join(context.getPhysicalPath()), 'depth': -1 }
            query['portal_type'] = 'ShopItemVariant'
            query['sort_on'] = 'getObjPositionInParent'

            results = {}
            mitems = ct(**query)
            for mitem in mitems:
                obj = mitem.getObject()
                key = obj.variantLabel
                if not results.has_key(key):
                    results[key] = list()
                results[key].append(dict(
                    order_number = obj.Schema().getField('skuCode').get(obj),
                    title = obj.Title(),
                    price = obj.Schema().getField('price').get(obj),
                    url = '%s/addtocart' % obj.absolute_url(),
                ))
            return results


class EditVariationsView(BrowserView):
    """View for editing ShopItem Variations
    """
    template = ViewPageTemplateFile('edit_variations.pt')

    def __call__(self):
        """
        Self-submitting form that displays ShopItem Variations
        and updates them
        
        """

        form = self.request.form

        # Make sure we had a proper form submit, not just a GET request
        submitted = form.get('form.submitted', False)
        if submitted:
            variation_config = IVariationConfig(self.context)
            shop_item = self.context
            variation_data = {}
            for var1_value in self.getVariation1Values():
                for var2_value in self.getVariation2Values():
                    variation_key = "%s-%s" % (var1_value, var2_value)
                    data = {}
                    data['active'] = bool(form.get("%s-active" % variation_key))
                    # TODO: Handle decimal correctly
                    price = form.get("%s-price" % variation_key)
                    try:
                        p = int(price)
                        # Create a tuple of ints from string
                        digits = tuple([int(i) for i in list(str(p))]) + (0, 0)
                        data['price'] = Decimal((0, digits, -2))
                    except ValueError:
                        if not price == "":
                            data['price'] = Decimal(price)
                        else:
                            data['price'] = Decimal("0.00")

                    data['stock'] = int(form.get("%s-stock" % variation_key))
                    data['skuCode'] = form.get("%s-skuCode" % variation_key)
                    variation_data[variation_key] = data
            #shop_item.variation_data = str(variation_data)
            variation_config.updateVariationConfig(variation_data)
            IStatusMessage(self.request).addStatusMessage(_("Variations saved."),
                                                                  type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())
                
        return self.template()

    def getVariationAttributes(self):
        variation_attributes = []
        if self.context.Schema().getField('variation1_attribute').get(self.context) not in (None, ''):
            variation_attributes.append(self.context.Schema().getField('variation1_attribute').get(self.context))
        if self.context.Schema().getField('variation2_attribute').get(self.context) not in (None, ''):
            variation_attributes.append(self.context.Schema().getField('variation2_attribute').get(self.context))
        return variation_attributes


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
        variation_config = IVariationConfig(self.context)
        variation_data= variation_config.getVariationConfig()

        #variation_data = eval(self.context.variation_data)
        variation_key = "%s-%s" % (var1_attr, var2_attr)
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

            