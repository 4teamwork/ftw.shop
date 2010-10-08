from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import ViewletBase
from ftw.shop.interfaces import IVariationConfig


class ShopItemListingViewlet(ViewletBase):
    render = ViewPageTemplateFile('shopitem_viewlet.pt')

    def getItemDatas(self):
        """Returns a dictionary of an item's properties to be used in
        templates. If the item has variations, the variation config is
        also included.
        """
        results = []
        for item in self.view.getItems():
            assert(item.portal_type == 'ShopItem')
            varConf = IVariationConfig(item)

            has_variations = varConf.hasVariations()

            image = None
            tag = None
            if has_variations:
                skuCode = None
                price = None
            else:
                varConf = None
                skuCode = item.Schema().getField('skuCode').get(item)
                price = item.Schema().getField('price').get(item)

            if image:
                tag = image.tag(scale='tile')

            results.append(
                dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    imageTag = tag,
                    variants = None,
                    order_number = skuCode,
                    price = price,
                    varConf = varConf,
                    hasVariations = has_variations))
        return results
