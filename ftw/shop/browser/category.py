from decimal import Decimal
import simplejson
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance

from ftw.shop.config import CATEGORY_RELATIONSHIP
from ftw.shop.interfaces import IShopItem
from ftw.shop.interfaces import IVariationConfig


class CategoryView(BrowserView):
    """Default view for a category. Shows all contained items and categories.
    """

    __call__ = ViewPageTemplateFile('templates/category.pt')

    single_item_template = ViewPageTemplateFile('templates/listing/single_item.pt')
    one_variation_template = ViewPageTemplateFile('templates/listing/one_variation_compact.pt')
    two_variations_template = ViewPageTemplateFile('templates/listing/two_variations_compact.pt')


    def getItems(self):
        """Returns a list of ShopItems directly contained in this category
        """
        return [item for item in self.category_contents
                if IShopItem.providedBy(item)]

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
            assert(IShopItem.providedBy(item))
            varConf = IVariationConfig(item)

            has_variations = varConf.hasVariations()

            image = item.getField('image')
            if image and image.get_size(item):
                hasImage = True
                tag = image.tag(item, scale='mini')
            else:
                hasImage = False
                tag = None
            if has_variations:
                skuCode = None
                price = None
            else:
                varConf = None
                skuCode = item.Schema().getField('skuCode').get(item)
                price = item.Schema().getField('price').get(item)

            results.append(
                dict(
                    item = item,
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    hasImage = hasImage,
                    imageTag = tag,
                    variants = None,
                    skuCode = skuCode,
                    price = price,
                    showPrice = item.getField('showPrice').get(item),
                    unit=item.getField('unit').get(item),
                    uid = item.UID(),
                    varConf = varConf,
                    hasVariations = has_variations,
                    selectable_dimensions = item.getSelectableDimensions()))
        return results

    def getVarDictsJSON(self):
        """Returns a JSON serialized dict with UID:varDict pairs, where UID
        is the ShopItem's UID and varDict is the item's variation dict.
        This is being used for the compact category view where inactive
        item variations must not be buyable.
        """
        varDicts = {}
        items = self.getItemDatas()
        for item in items:
            uid = item['uid']
            varConf = item['varConf']
            if varConf is not None:
                varDicts[uid] = dict(varConf.getVariationDict())
            else:
                varDicts[uid] = {}

            # Convert Decimals to Strings for serialization
            varDict = varDicts[uid]
            for vcode in varDict.keys():
                i = varDict[vcode]
                for k in i.keys():
                    val = i[k]
                    if isinstance(val, Decimal):
                        val = str(val)
                        i[k] = val

        return simplejson.dumps(varDicts)

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
        def filter_language(item):
            """Return ``True`` for items that have the same language as the
               context or items that have no language.
            """
            language = context.Language()
            if not item.Language():
                return True
            if item.Language()==language:
                return True
            return False

        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')

        contents = context.getBRefs(CATEGORY_RELATIONSHIP)

        contents = [item for item in contents
                    if item and mtool.checkPermission('View', item)
                    and filter_language(item)]

        # Sort alphabetically first
        contents.sort(key=lambda x: x.Title())

        # Then by ranking
        contents.sort(lambda x, y: cmp(x.getRankForCategory(context),
                        y.getRankForCategory(context)))
        return contents
