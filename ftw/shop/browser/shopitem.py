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
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


class ShopItemView(BrowserView):
    """Default view for a shop item
    """
    
    __call__ = ViewPageTemplateFile('shopitem.pt')
    
    @property
    @instance.memoize    
    def item(self):
        context = aq_inner(self.context)
        has_variations = context.Schema().getField('variation1_attribute').get(context) not in (None, '')
        skuCode = context.Schema().getField('skuCode').get(context)
        if not has_variations:
            return dict(
                order_number = skuCode,
                price = context.Schema().getField('price').get(context),
                url = '%s/addtocart?skuCode=%s' % (context.absolute_url(), skuCode),
            )
        return None

    @property
    @instance.memoize
    def variations(self):
        context = aq_inner(self.context)
        variation_config = IVariationConfig(self.context)
        has_variations = context.Schema().getField('variation1_attribute').get(context) not in (None, '')
        if has_variations:
            return variation_config.getVariationConfig()


    def getVariationsConfig(self):
        context = aq_inner(self.context)
        variation_config = IVariationConfig(self.context)
        return variation_config


    def getVariationAttributes(self):
        variation_attributes = []
        if self.context.Schema().getField('variation1_attribute').get(self.context) not in (None, ''):
            variation_attributes.append(self.context.Schema().getField('variation1_attribute').get(self.context))
        if self.context.Schema().getField('variation2_attribute').get(self.context) not in (None, ''):
            variation_attributes.append(self.context.Schema().getField('variation2_attribute').get(self.context))
        return variation_attributes


class EditVariationsView(ShopItemView):
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
            
            edited_var_data = self._parse_edit_variations_form()
            variation_config.updateVariationConfig(edited_var_data)

            IStatusMessage(self.request).addStatusMessage(
                _("Variations saved."), type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.template()



    def _parse_edit_variations_form(self):
        form = self.request.form
        variation_config = IVariationConfig(self.context)
        variation_data = {}
        normalizer = getUtility(IIDNormalizer)

        for var1_value in variation_config.getVariation1Values():
            for var2_value in variation_config.getVariation2Values():
                variation_key = normalizer.normalize("%s-%s" % (var1_value, var2_value))
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
        return variation_data

            