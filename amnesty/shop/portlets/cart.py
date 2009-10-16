from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize 

class ICartPortlet(IPortletDataProvider):
    """A portlet that displays the shopping cart
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICartPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Cart Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('cart.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.navroot_url = portal_state.navigation_root_url()
        
    @property 
    def available(self):
        return len(self.cart_items())>0

    @memoize
    def cart_items(self):
        """ get a list of shop items in cart
        """
        cart_view = getMultiAdapter((self.context, self.request), name=u'cart_view')
        return cart_view.cart_items()


