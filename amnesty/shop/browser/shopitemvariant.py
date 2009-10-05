from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
     
class ShopItemVariantView(BrowserView):
    """Redirect to parent for users not having permission to edit the item.
       Render base_view if user has edit permissions.
    """
    #implements(IAIArticleView)
    
    def __call__(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        if mtool.checkPermission('Modify portal content', context):
            return context.base_view()
        self.request.response.redirect(aq_parent(context).absolute_url())