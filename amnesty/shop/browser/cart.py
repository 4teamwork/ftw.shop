from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from amnesty.shop import shopMessageFactory as _
from amnesty.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation

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
                    'url': context.absolute_url(),
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

    def cart_items(self):
        """ get content of shopping cart
        """
        context = aq_inner(self.context)
        session = self.request.SESSION
        items = session.get(CART_KEY, {})
        return items

    def cart_total(self):
        """
        """
        items = self.cart_items()
        total = 0.0
        for item in items.values():
            total += item['total']
        return total
        
    def checkout(self):
       """ process checkout
       """
       context = aq_inner(self.context)
       ptool = getToolByName(context, 'plone_utils')
       url = context.absolute_url()
       
       # check if we have something in the cart
       items = self.cart_items()
       if not items:
           ptool.addPortalMessage(_(u'msg_no_cart', default=u"Can't proceed with empty cart."), 'error')
           self.request.response.redirect(url)
           
       omanager = getToolByName(context, 'portal_ordermanager')
       order_id = ''
       try:
           order_id = omanager.addOrder()
       except MissingCustomerInformation:
           self.request.response.redirect('%s/customer' % url)
           return
       except MissingOrderConfirmation:
           self.request.response.redirect('%s/order_review' % url)
           return
           
       self.request.SESSION.invalidate()
       self.request.response.redirect('%s/thankyou?order_id=%s' % (url, order_id))
       return
