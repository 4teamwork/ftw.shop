from ftw.shop import portlets
from ftw.shop import shopMessageFactory as _
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility


class InitShopStructure(BrowserView):
    """Set up an initial folder structure for the shop
    """

    def __call__(self):
        portal_url = getToolByName(self.context, "portal_url")
        ptool = getToolByName(self.context, 'plone_utils')

        portal = portal_url.getPortalObject()
        shop = getattr(portal, 'shop', None)
        if not shop:
            portal.invokeFactory('Folder', 'shop', title='Shop')
            shop = portal.shop

        # Add Shopping Cart portlet to Shop Root
        column = getUtility(IPortletManager,
                            name=u'plone.rightcolumn',
                            context=shop)
        manager = getMultiAdapter((shop, column), IPortletAssignmentMapping)
        if 'ftw.shop.portlets.cart' not in manager.keys():
            manager['ftw.shop.portlets.cart'] = portlets.cart.Assignment()

        ptool.addPortalMessage(_(u'msg_shop_initialized',
                                 default=u"Shop structure initialized."),
                               'info')
        # redirect to referer
        referer = self.request.get('HTTP_REFERER', portal.absolute_url())
        if not referer in ['', 'localhost']:
            self.request.response.redirect(referer)
        else:
            self.request.response.redirect(portal.absolute_url())
        return
