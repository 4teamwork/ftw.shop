from Products.Five.browser import BrowserView
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IVariationConfig
from ftw.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation
from decimal import Decimal
from ftw.shop.root import get_shop_root_object


CART_KEY = 'shop_cart_items'


class CartView(BrowserView):
    """
    """
    
    def addtocart(self, skuCode):
        """ add item to cart and redirect to referer
        """
        context = aq_inner(self.context)

                
        # get current items in cart
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        item = cart_items.get(skuCode, None)
        item_title = context.Title()

        has_variations = context.Schema().getField('variation1_attribute').get(context) not in (None, '')
        if has_variations:
            variation_config = IVariationConfig(self.context)
            variation_data = variation_config.getVariationConfig()
            variation_key = None
            for vkey in variation_data.keys():
                if variation_data[vkey]['skuCode'] == skuCode:
                    variation_key = vkey
                    break

            item_title = '%s - %s' % (context.Title(), variation_key)
            price = Decimal(variation_data[variation_key]['price'])
            # add item to cart
            if item is None:
                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity':1,
                        'price': str(price),
                        'total': str(price),
                        'url': context.absolute_url(),
                        'variation_key': variation_key,
                }    
            # item already in cart, update quantitiy
            else:
                item['quantity'] = item.get('quantity', 0) + 1
                item['total'] = str(item['quantity'] * price)
                
        else:
            price = Decimal(context.Schema().getField('price').get(context))
            # add item to cart
            if item is None:
                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity':1,
                        'price': str(price),
                        'total': str(price),
                        'url': context.absolute_url(),
                }    
            # item already in cart, update quantitiy
            else:
                item['quantity'] = item.get('quantity', 0) + 1
                item['total'] = str(item['quantity'] * price)


        # store cart in session    
        cart_items[skuCode] = item
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

    def remove_item(self, skuCode):
        """ remove item by skuCode from cart.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        
        if cart_items.has_key(skuCode):
            del cart_items[skuCode]
            
        session[CART_KEY] = cart_items  

    def update_item(self, skuCode, quantity):
        """ update the quantity of an item.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        
        if cart_items.has_key(skuCode):
            item = cart_items[skuCode]
            item['quantity'] = int(quantity)
            item['total'] = str(Decimal(item['price']) * item['quantity'])
            cart_items[skuCode] = item
            
        session[CART_KEY] = cart_items
        
    def cart_update(self):
        """ update cart contents.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        
        # first delete items with quantity 0
        del_items = []
        for skuCode in self.cart_items().keys():
            try:
                quantity = int(float(self.request.get('quantity_%s' % skuCode)))
                if quantity == 0:
                    del_items.append(skuCode)
            except ValueError:
                ptool.addPortalMessage(_(u'msg_cart_invalidvalue', default=u"Invalid Values specified. Cart was not updated."), 'error')
                referer = self.request.get('HTTP_REFERER', context.absolute_url())
                self.request.response.redirect(referer)
                return
        for skuCode in del_items:
            self.remove_item(skuCode)
        
        # now update quantities    
        for skuCode,item in self.cart_items().items():
            quantity = int(float(self.request.get('quantity_%s' % skuCode)))
            if quantity != item['quantity'] and quantity != 0:
                self.update_item(skuCode, quantity)

        ptool.addPortalMessage(_(u'msg_cart_updated', default=u"Cart updated."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return 

    def cart_remove(self):
        """ remove an item from cart.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        skuCode = self.request.get('skuCode')
        if skuCode:
            self.remove_item(skuCode)
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
        context = aq_inner(self.context)
        shop_root = get_shop_root_object(context)
        return shop_root.absolute_url()
