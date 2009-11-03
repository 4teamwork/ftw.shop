from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from amnesty.shop import shopMessageFactory as _
from amnesty.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation
from decimal import Decimal
from zope.component import getMultiAdapter

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
        price = Decimal(context.Price())
        # add item to cart
        if item is None:
            item = {'title': item_title,
                    'description': context.Description(),
                    'skucode': context.getSku_code(),
                    'quantity':1,
                    'price': str(price),
                    'currency': context.getCurrency(),
                    'total': str(price),
                    'url': context.absolute_url(),
            }    
        # item already in cart, update quantitiy
        else:
            item['quantity'] = item.get('quantity', 0) + 1
            item['total'] = str(item['quantity'] * price)
        

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
        total = Decimal('0.00')
        for item in items.values():
            total += Decimal(item['total'])
        return str(total)

    def remove_item(self, uid):
        """ remove item by uid from cart.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        
        if cart_items.has_key(uid):
            del cart_items[uid]
            
        session[CART_KEY] = cart_items  

    def update_item(self, uid, quantity):
        """ update the quantity of an item.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        
        if cart_items.has_key(uid):
            item = cart_items[uid]
            item['quantity'] = int(quantity)
            item['total'] = str(Decimal(item['price']) * item['quantity'])
            cart_items[uid] = item
            
        session[CART_KEY] = cart_items
        
    def cart_update(self):
        """ update cart contents.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        
        # first delete items with quantity 0
        del_items = []
        for uid in self.cart_items().keys():
            try:
                quantity = int(float(self.request.get('quantity_%s' % uid)))
                if quantity == 0:
                    del_items.append(uid)
            except ValueError:
                ptool.addPortalMessage(_(u'msg_cart_invalidvalue', default=u"Invalid Values specified. Cart was not updated."), 'error')
                referer = self.request.get('HTTP_REFERER', context.absolute_url())
                self.request.response.redirect(referer)
                return
        for uid in del_items:
            self.remove_item(uid)
        
        # now update quantities    
        for uid,item in self.cart_items().items():
            quantity = int(float(self.request.get('quantity_%s' % uid)))
            if quantity != item['quantity'] and quantity != 0:
                self.update_item(uid, quantity)

        ptool.addPortalMessage(_(u'msg_cart_updated', default=u"Cart updated."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return 

    def cart_remove(self):
        """ remove an item from cart.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        uid = self.request.get('uid')
        if uid:
            self.remove_item(uid)
            ptool.addPortalMessage(_(u'msg_cart_updated', default=u"Cart updated."), 'info')
            
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return 
        
        
    def cart_delete(self):
        """ remove all items from cart.
        """
        session = self.request.SESSION
        session[CART_KEY] = {}
        
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        ptool.addPortalMessage(_(u'msg_cart_emptied', default=u"Cart emptied."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return
        
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

    def shop_url(self):
        """ return the root url of the shop folder.
        """
        # pretty hard coded now. maybe we should use a marker interface instead...
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        navroot_url = portal_state.navigation_root_url()
        if navroot_url.endswith('fr'):
            return '%s/boutique' % navroot_url
        else:
            return '%s/shop' % navroot_url
