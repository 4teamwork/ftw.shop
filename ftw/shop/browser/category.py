from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance

from ftw.shop.config import CATEGORY_RELATIONSHIP
from ftw.shop.interfaces import IVariationConfig


class CategoryView(BrowserView):
    """Default view for a category. Shows all contained items and categories.
    """

    __call__ = ViewPageTemplateFile('templates/category.pt')

    single_item_template = ViewPageTemplateFile('templates/listing/single_item.pt')
    one_variation_template = ViewPageTemplateFile('templates/listing/one_variation.pt')
    two_variations_template = ViewPageTemplateFile('templates/listing/two_variations.pt')

    def getItems(self):
        """Returns a list of ShopItems directly contained in this category
        """
        return [item for item in self.category_contents
                if item.portal_type == 'ShopItem']

    def single_item(self, item):
        return self.single_item_template(item=item)

    def one_variation(self, item):
        return self.one_variation_template(item=item)

    def two_variations(self, item):
        return self.two_variations_template(item=item)

    def getItemDatas(self):
        """Returns a dictionary of an item's properties to be used in
        templates. If the item has variations, the variation config is
        also included.
        """
        results = []
        for item in self.getItems():
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
                    skuCode = skuCode,
                    price = price,
                    varConf = varConf,
                    hasVariations = has_variations))
        return results

    @property
    @instance.memoize
    def categories(self):
        """ get a list with all categories belonging to this category.
        """
        results = []
        for item in self.category_contents:
            image = None
            tag = None
            if image:
                tag = image.tag(scale='tile')
            if item.portal_type == 'ShopCategory':
                results.append(dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    image = tag,
                ))
        return results

    @property
    @instance.memoize
    def category_contents(self):
        """ get all items (shop items, categories) belonging to this category.
        """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')

        contents = context.getBRefs(CATEGORY_RELATIONSHIP)

        contents = [item for item in contents
                    if mtool.checkPermission('View', item)]
        contents.sort(lambda x, y: cmp(x.getRankForCategory(context),
                        y.getRankForCategory(context)))
        return contents

#    TODO: Check if still needed and replace with edit_categories
#    def manage_categories(self):
#        return getMultiAdapter((self.context, self.request),
#                               'manage_categories')


class CategoryCompactView(CategoryView):
    """Compact view for a category. Shows all contained items and categories.
    """

    one_variation_template = ViewPageTemplateFile('templates/listing/one_variation_compact.pt')
    two_variations_template = ViewPageTemplateFile('templates/listing/two_variations_compact.pt')
