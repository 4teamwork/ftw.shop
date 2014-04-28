from Acquisition import aq_parent
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopCategory
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage


class ManageCategories(BrowserView):

    template = ViewPageTemplateFile('templates/edit_categories.pt')

    def __call__(self):
        """
        Self-submitting form that lets the user edit categories that
        ShopItems or ShopCategories belong to
        """
        form = self.request.form

        # Make sure we had a proper form submit, not just a GET request
        submitted = form.get('form.submitted', False)
        if submitted:
            edited_category_data = self.request.get('categories', [])
            self.update_categories(edited_category_data)
            IStatusMessage(self.request).addStatusMessage(
                _(u'msg_categories_updated',
                  default=u"Categories updated."), type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.template()

    def update_categories(self, categories):
        """Update the categories a ShopItem or ShopCategory belongs to
        """
        #categories = self.request.get('categories', None)
        old_uids = [obj.UID() for obj in self.context.listCategories()]

        # add the checked categories
        new_uids = [uid for uid in categories if uid not in old_uids]
        for c in new_uids:
            self.context.addToCategory(c)

        # remove the unchecked categories
        uids_delete = [uid for uid in old_uids if uid not in categories]
        categories_delete = uids_delete
        for c in categories_delete:
            self.context.removeFromCategory(c)

        #update ranks
        for c in self.context.listCategories():
            rank = self.context.REQUEST.get('rank_%s' % c.UID(), 1)
            self.context.setRankForCategory(c, rank)

        putils = getToolByName(self.context, 'plone_utils')
        putils.addPortalMessage(_(u'msg_categories_updated',
                                  default=u"Categories updated."), 'info')
        return self.context.REQUEST.RESPONSE.redirect('%s' %
                                            (self.context.absolute_url()))

    def find_first_non_category(self):
        """Walk up from the current context and find the first object that
        isn't of type ShopCategory.
        """
        # Start with the ShopItem's parent (which is a ShopCategory)
        parent = aq_parent(self.context)
        while IShopCategory.providedBy(parent):
            parent = aq_parent(parent)
        return parent

    def get_top_level_categories(self):
        """Walking up from current context, find the top level categories
        defining the start of a shop category sub-structure.
        """
        category_tree_container = self.find_first_non_category()

        catalog = getToolByName(self.context, 'portal_catalog')
        query = dict(
            object_provides=IShopCategory.__identifier__,
            path = {
                'query': '/'.join(category_tree_container.getPhysicalPath()),
                'depth': 1},
            sort_on = 'path',
            )
        categories = [b.getObject() for b in catalog(query)]
        return categories

    def get_sub_categories(self, context):
        """Given a ShopCategory as `context`, return all its subcategories.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        query = dict(
            object_provides=IShopCategory.__identifier__,
            path = {
                'query': '/'.join(context.getPhysicalPath()),
                },
            sort_on = 'path',
            )
        categories = [b.getObject() for b in catalog(query)]
        # Don't include the queried context itself
        categories.remove(context)
        return categories

    def list_all_categories(self, categoryUID):
        """return all Category instances except the context
        (that could be a Category instance too).
        """
        categoryUID = self.request.get('CategoryUID', None)
        #portalPath = getToolByName(self.context, 'portal_url').getPortalPath()
        #ltool = getToolByName(self.context, 'portal_languages')
        catalog = getToolByName(self.context, 'portal_catalog')
        #lang = ltool.getPreferredLanguage()

        query = {}
        query['portal_type'] = ['ShopCategory']
        #query['path'] = '%s/%s' % (portalPath, lang)
        query['sort_on'] = 'fullTitle'

        categories = catalog(query)
        return [category.getObject() for category in categories
                                        if category.UID != categoryUID]
