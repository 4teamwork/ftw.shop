from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from ftw.shop import shopMessageFactory as _


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
