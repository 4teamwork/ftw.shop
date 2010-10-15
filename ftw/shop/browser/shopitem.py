from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IVariationConfig
from decimal import Decimal
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


class ShopItemView(BrowserView):
    """Default view for a shop item
    """

    __call__ = ViewPageTemplateFile('templates/shopitem.pt')

    def getItems(self):
        """Returns a list with this item as its only element,
        so the listing viewlet can treat it like a list of items
        """
        context = aq_inner(self.context)
        return [context]

    def getVariationsConfig(self):
        """Returns the variation config for the item currently being viewed
        """
        context = aq_inner(self.context)
        variation_config = IVariationConfig(context)
        return variation_config


class ShopCompactItemView(BrowserView):
    """Compact view for a shop item
    """

    __call__ = ViewPageTemplateFile('templates/shopitem_compact.pt')

    def getItems(self):
        """Returns a list with this item as its only element,
        so the listing viewlet can treat it like a list of items
        """
        context = aq_inner(self.context)
        return [context]

    def getVariationsConfig(self):
        """Returns the variation config for the item currently being viewed
        """
        context = aq_inner(self.context)
        variation_config = IVariationConfig(context)
        return variation_config


class EditVariationsView(BrowserView):
    """View for editing ShopItem Variations
    """
    template = ViewPageTemplateFile('templates/edit_variations.pt')

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
                _(u'msg_variations_saved', default=u"Variations saved."), type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.template()

    def _parse_edit_variations_form(self):
        """Parses the form the user submitted when editing variations,
        and returns a dictionary that contains the variation data.
        """
        form = self.request.form
        variation_config = IVariationConfig(self.context)
        variation_data = {}
        normalizer = getUtility(IIDNormalizer)
        
        # TODO: Refactor this to avoid code duplication
        
        if len(variation_config.getVariationAttributes()) == 1:
            for var1_value in variation_config.getVariation1Values():
                variation_key = normalizer.normalize(var1_value)
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
        else:
            for var1_value in variation_config.getVariation1Values():
                for var2_value in variation_config.getVariation2Values():
                    variation_key = normalizer.normalize(
                                        "%s-%s" % (var1_value, var2_value))
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

    def getVariationsConfig(self):
        """Returns the variation config for the item being edited
        """
        context = aq_inner(self.context)
        variation_config = IVariationConfig(context)
        return variation_config
