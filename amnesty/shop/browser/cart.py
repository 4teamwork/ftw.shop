from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from amnesty.shop import shopMessageFactory as _

CART_KEY = 'shop_cart_items'

class CartView(BrowserView):
    """
    """
    
    def addtocart(self):
        """ add item to cart and redirect to referer
        """
        context = aq_inner(self.context)
                
        # get current items in cart
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        
        item_title = context.Title()
        if context.portal_type == 'ShopItemVariant':
            parent = aq_parent(context)
            item_title = '%s - %s' % (parent.Title(), item_title)
            
        item_uid = context.UID()
        item = cart_items.get(item_uid, None)
        # add item to cart
        if item is None:
            item = {'title': item_title,
                    'quantity':1,
                    'price': float(context.Price()),
                    'currency': context.getCurrency(),
                    'total': float(context.Price()),
            }    
        # item already in cart, update quantitiy
        else:
            item['quantity'] = item.get('quantity', 0) + 1
            item['total'] = item['quantity'] * item['price']
        

        # store cart in session    
        cart_items[item_uid] = item
        session[CART_KEY] = cart_items  
        
        # add portal message
        ptool = getToolByName(context, 'plone_utils')
        ptool.addPortalMessage(_(u'msg_item_added', default=u'Added item to cart.'), 'info')
        
        # redirect to referer
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
