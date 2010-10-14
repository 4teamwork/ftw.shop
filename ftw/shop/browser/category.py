from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from plone.memoize import instance
from Acquisition import aq_inner
from ftw.shop.config import CATEGORY_RELATIONSHIP
from Products.CMFCore.utils import getToolByName


class CategoryView(BrowserView):
    """Default view for a category. Shows all contained items and categories.
    """

    __call__ = ViewPageTemplateFile('templates/category.pt')

    def dummyitems(self):
        return []

    def getItems(self):
        """Returns a list of ShopItems directly contained in this category
        """
        context = aq_inner(self.context)
        return [item for item in self.category_contents
                if item.portal_type == 'ShopItem']

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
    
    def manage_categories(self):
        return getMultiAdapter((self.context, self.request), 'manage_categories')
