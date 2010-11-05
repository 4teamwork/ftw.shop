from decimal import Decimal
import simplejson

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapters, getMultiAdapter

from ftw.shop.config import CART_KEY
from ftw.shop.config import SESSION_ADDRESS_KEY, ONACCOUNT_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.interfaces import IVariationConfig
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.root import get_shop_root_object
from ftw.shop import shopMessageFactory as _


class CartView(BrowserView):
    """Handles the customer's shopping cart and stores it in the user's
    session.
    This view is responsible for adding, updating and removing items from 
    the cart, as well as calculating the current cart total.
    """
    portlet_template = ViewPageTemplateFile('../portlets/cart.pt')

    def addtocart_ajax(self, skuCode=None, quantity=1,
                       var1choice=None, var2choice=None):
        """ Add item to cart, return portlet HTML and translated status
        message
        """
        self._addtocart(skuCode, quantity, var1choice, var2choice)
        translate = self.context.translate

        status_msg_label = _(u'msg_label_info', default=u"Information")
        status_msg_text = _(u'msg_item_added', default=u"Added item to cart.")
        status_message = """
            <dt>%s</dt>
            <dd>%s</dd>
        """ % (translate(status_msg_label),
               translate(status_msg_text))

        return simplejson.dumps(dict(portlet_html=self.portlet_template(),
                    status_message=status_message))

    def addtocart(self, skuCode=None, quantity=1,
                  var1choice=None, var2choice=None):
        """Add item to cart and redirect to referer.

        The item must be identified by either its skuCode if it is an item
        without variations, or by its variation key.
        """
        context = aq_inner(self.context)

        # Add item to cart
        self._addtocart(skuCode, quantity, var1choice, var2choice)

        # redirect to referer
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)

        # add portal message
        ptool = getToolByName(context, 'plone_utils')
        ptool.addPortalMessage(_(u'msg_item_added',
                                 default=u'Added item to cart.'), 'info')

    def _addtocart(self, skuCode=None, quantity=1,
                   var1choice=None, var2choice=None):
        """ Add item to cart
        """
        context = aq_inner(self.context)
        varConf = IVariationConfig(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        # get current items in cart
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        if not skuCode:
            # We got no skuCode, so look it up by variation key
            skuCode = varConf.getVariationData(var1choice,
                                               var2choice,
                                               'skuCode')

        item = cart_items.get(skuCode, None)

        item_title = context.Title()
        quantity = int(quantity)
        
        # If available, get supplier name and email address
        supplier_name = ''
        supplier_email = ''
        if context.getField('supplier') is not None:
            supplier = context.getField('supplier').get(context)
            if supplier is not None:
                supplier_name = supplier.getField('title').get(supplier)
                supplier_email = supplier.getField('email').get(supplier)

        has_variations = varConf.hasVariations()
        if has_variations:
            variation_dict = varConf.getVariationDict()
            variation_key = None
            for vkey in variation_dict.keys():
                if variation_dict[vkey]['skuCode'] == skuCode:
                    variation_key = vkey
                    break

            variation_pretty_name = varConf.getPrettyName(variation_key)
            item_title = '%s - %s' % (context.Title(), variation_pretty_name)
            price = Decimal(variation_dict[variation_key]['price'])
            # add item to cart
            if item is None:

                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'total': str(price * quantity),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                        'variation_key': variation_key,
                }
            # item already in cart, update quantity
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                item['total'] = str(item['quantity'] * price)

        else:
            price = Decimal(context.Schema().getField('price').get(context))
            # add item to cart
            if item is None:
                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'total': str(price * quantity),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                }
            # item already in cart, update quantitiy
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                item['total'] = str(item['quantity'] * price)


        # store cart in session
        cart_items[skuCode] = item
        session[CART_KEY] = cart_items
        session['foobar'] = 'barfoo'

    def cart_items(self):
        """Get all items currently contained in shopping cart
        """
        session = self.request.SESSION
        items = session.get(CART_KEY, {})
        return items

    def cart_total(self):
        """Return the cart's total as a string
        """
        items = self.cart_items()
        total = Decimal('0.00')
        for item in items.values():
            total += Decimal(item['total'])
        return str(total)

    def remove_item(self, skuCode):
        """Remove item from cart by skuCode.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        if skuCode in cart_items:
            del cart_items[skuCode]

        session[CART_KEY] = cart_items

    def update_item(self, skuCode, quantity):
        """Update the quantity of an item.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        if skuCode in cart_items:
            item = cart_items[skuCode]
            item['quantity'] = int(quantity)
            item['total'] = str(Decimal(item['price']) * item['quantity'])
            cart_items[skuCode] = item

        session[CART_KEY] = cart_items

    def cart_update(self):
        """Update cart contents.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')

        # first delete items with quantity 0
        del_items = []
        for skuCode in self.cart_items().keys():
            try:
                qty = int(float(self.request.get('quantity_%s' % skuCode)))
                if qty == 0:
                    del_items.append(skuCode)
            except ValueError:
                ptool.addPortalMessage(
                    _(u'msg_cart_invalidvalue',
                      default=u"Invalid Values specified. Cart not updated."),
                    'error')
                referer = self.request.get('HTTP_REFERER',
                                           context.absolute_url())
                self.request.response.redirect(referer)
                return
        for skuCode in del_items:
            self.remove_item(skuCode)

        # now update quantities
        for skuCode, item in self.cart_items().items():
            quantity = int(float(self.request.get('quantity_%s' % skuCode)))
            if quantity != item['quantity'] and quantity != 0:
                self.update_item(skuCode, quantity)

        ptool.addPortalMessage(_(u'msg_cart_updated',
                                 default=u"Cart updated."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return

    def cart_remove(self):
        """Remove an item from cart.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        skuCode = self.request.get('skuCode')
        if skuCode:
            self.remove_item(skuCode)
            ptool.addPortalMessage(_(u'msg_cart_updated',
                                     default=u"Cart updated."), 'info')

        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return

    def cart_delete(self):
        """Remove all items from cart.
        """
        session = self.request.SESSION
        session[CART_KEY] = {}

        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        ptool.addPortalMessage(_(u'msg_cart_emptied',
                                 default=u"Cart emptied."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return

    def checkout(self):
        """Process checkout
        """
        context = aq_inner(self.context)
        session = context.REQUEST.SESSION
        ptool = getToolByName(context, 'plone_utils')
        url = context.absolute_url()

        # check if we have something in the cart
        items = self.cart_items()
        if not items:
            ptool.addPortalMessage(_(u'msg_no_cart',
                            default=u"Can't proceed with empty cart."),
                'error')
            self.request.response.redirect(url)

        omanager = getMultiAdapter((context, self.request),
                                   name=u'order_manager')

        # Check we got all the data we need from the wizard
        try:
            order_id = omanager.addOrder()
        except MissingCustomerInformation:
            self.request.response.redirect('%s/checkout-wizard' % url)
            return
        except MissingOrderConfirmation:
            self.request.response.redirect('%s/checkout-wizard' % url)
            return
        except MissingPaymentProcessor:
            self.request.response.redirect('%s/checkout-wizard' % url)
            return

        # Get the payment processor selected by the customer
        payment_processor_name = session.get(
            'payment_processor_choice').get('payment_processor')
        for name, adapter in getAdapters((context, None, context),
                                         IPaymentProcessor):
            if name == payment_processor_name:
                payment_processor = adapter

        if not payment_processor_name or not payment_processor.external:
            # No payment processor step at all OR payment by invoice

            customer_info = self.request.SESSION[SESSION_ADDRESS_KEY]
            self.request.SESSION.invalidate()

            # Get a new session object, since the old one still returns
            # stale data even though it has been invalidated
            session = context.session_data_manager.getSessionData()
            session[SESSION_ADDRESS_KEY] = customer_info

            # Set correct status for payment by invoice
            order = omanager.getOrder(order_id)
            order.status = ONACCOUNT_KEY

            omanager.sendOrderMail(order_id)

            self.request.response.redirect(
                        '%s/thankyou?order_id=%s' % (url, order_id))
            return
        else:
            #self.request.SESSION.invalidate()
            self.request.SESSION['order_id'] = order_id
            pp_launch_page = 'external-payment-processor'
            pp_launch_page = payment_processor.launch_page
            self.request.response.redirect('%s/%s' % (url, pp_launch_page))
            return

    def shop_url(self):
        """Return the root url of the shop folder.
        """
        context = aq_inner(self.context)
        shop_root = get_shop_root_object(context)
        return shop_root.absolute_url()
