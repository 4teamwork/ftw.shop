from Acquisition import aq_inner, aq_parent
from decimal import Decimal
from ftw.shop import shopMessageFactory as _
from ftw.shop.config import CART_KEY
from ftw.shop.config import SESSION_ADDRESS_KEY, ONACCOUNT_KEY
from ftw.shop.exceptions import MissingCustomerInformation
from ftw.shop.exceptions import MissingOrderConfirmation
from ftw.shop.exceptions import MissingPaymentProcessor
from ftw.shop.exceptions import MissingShippingAddress
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IShoppingCart
from ftw.shop.interfaces import IVariationConfig
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
import simplejson


def calc_vat(rate, price, qty=1):
    """Calculate VAT and round to correct precision.
    """
    vat_amount = (Decimal(rate)/100) * Decimal(price) * qty
    vat_amount = vat_amount.quantize(Decimal('.01'))
    return vat_amount


class ShoppingCartAdapter(object):
    """Adapter that represents the shopping cart for the current user, defined
    by the adapted context and request.

    This adapter is responsible for adding, updating and removing items from the
    cart and storing that information in the user's session, as well as
    calculating the current cart total.
    """
    implements(IShoppingCart)
    adapts(Interface, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = getToolByName(self.context, 'portal_catalog')
        return self._catalog

    def get_items(self):
        """Get all items currently contained in shopping cart
        """
        # Avoid creating a session if there doesn't exist one yet.
        bid_manager = getToolByName(self.context, 'browser_id_manager')
        browser_id = bid_manager.getBrowserId(create=0)
        if not browser_id:
            return {}
        session = self.request.SESSION
        items = session.get(CART_KEY, {})
        return items

    def get_vat(self):
        """Return the cart's total VAT as a string
        """
        items = self.get_items()
        vat_total = Decimal('0.00')
        for item in items.values():
            vat_total += Decimal(item['vat_amount'])
        return str(vat_total)

    def get_total(self):
        """Return the cart's total as a string
        """
        items = self.get_items()
        total = Decimal('0.00')
        for item in items.values():
            total += Decimal(item['total'])
        return str(total)

    def _get_supplier_info(self, context):
        supplier = self._get_supplier(context)
        if supplier:
            supplier_name = supplier.getField('title').get(supplier)
            supplier_email = supplier.getField('email').get(supplier)
            return supplier_name, supplier_email
        return ('', '')

    def _get_supplier(self, context):
        """If available, get supplier name and email address
        """
        supplier = None

        while not INavigationRoot.providedBy(context):
            field = context.getField('supplier')
            if field is not None:
                supplier = field.get(context)

                if supplier:
                    break

            context = aq_parent(aq_inner(context))

        return supplier

    def get_suppliers(self):
        suppliers = []

        for itemkey, itemvalue in self.get_items().items():
            if 'variation_code' in itemvalue:
                uid = itemkey.rstrip(itemvalue['variation_code'].strip('var'))
            else:
                uid = itemkey

            item = self.catalog(UID=uid)[0].getObject()
            supplier = self._get_supplier(item)
            suppliers.append(supplier)
        return suppliers

    def get_show_prices(self):
        for item in self.get_items().values():
            if item['show_price']:
                return True
        return False

    def has_single_supplier(self):
        """Returns true if all the suppliers are the same, or there are no
        suppliers whatsoever.
        """
        suppliers = self.get_suppliers()
        return all(x == suppliers[0] for x in suppliers)

    def update_item(self, key, quantity):
        """Update the quantity of an item.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        if key in cart_items:
            item = cart_items[key]
            item['quantity'] = int(quantity)
            item['total'] = str(Decimal(item['price']) * item['quantity'])
            item['vat_amount'] = str(calc_vat(item['vat_rate'], item['price'], quantity))
            cart_items[key] = item

        session[CART_KEY] = cart_items

    def _add_item(self, skuCode=None, quantity=1,
                   var1choice=None, var2choice=None):
        """ Add item to cart
        """
        context = aq_inner(self.context)
        varConf = IVariationConfig(self.context)

        # get current items in cart
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})
        variation_code = varConf.variation_code(var1choice, var2choice)

        # We got no skuCode, so look it up by variation key
        if not skuCode:
            skuCode = varConf.sku_code(var1choice, var2choice)

        item_key = varConf.key(var1choice, var2choice)
        item = cart_items.get(item_key, None)

        item_title = context.Title()
        quantity = int(quantity)
        vat_rate = Decimal(context.getField('vat').get(context))

        supplier_name, supplier_email = self._get_supplier_info(context)

        has_variations = varConf.hasVariations()
        if has_variations:
            variation_dict = varConf.getVariationDict()
            if not variation_dict[variation_code]['active']:
                # Item is disabled
                return False

            variation_pretty_name = varConf.getPrettyName(variation_code)
            item_title = '%s - %s' % (context.Title(), variation_pretty_name)
            price = Decimal(variation_dict[variation_code]['price'])
            # add item to cart
            if item is None:

                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'show_price': context.showPrice,
                        'total': str(price * quantity),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                        'variation_code': variation_code,
                        'vat_rate': vat_rate,
                        'vat_amount': str(calc_vat(vat_rate, price))
                }
            # item already in cart, update quantity
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                item['total'] = str(item['quantity'] * price)
                item['vat_amount'] = str(calc_vat(vat_rate, price, quantity))

        else:
            price = Decimal(context.Schema().getField('price').get(context))
            # add item to cart
            if item is None:

                item = {'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'show_price': context.showPrice,
                        'total': str(price * quantity),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                        'vat_rate': vat_rate,
                        'vat_amount': str(calc_vat(vat_rate, price))
                }
            # item already in cart, update quantitiy
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                item['total'] = str(item['quantity'] * price)
                item['vat_amount'] = str(calc_vat(vat_rate, price, quantity))

        # store cart in session
        cart_items[item_key] = item
        session[CART_KEY] = cart_items
        return True

    def add_item(self, skuCode=None, quantity=1,
                 var1choice=None, var2choice=None):
        """Add item to cart and redirect to referer.

        The item must be identified by either its skuCode if it is an item
        without variations, or by its variation key.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')

        # Add item to cart
        success = self._add_item(skuCode, quantity, var1choice, var2choice)
        if success:
            ptool.addPortalMessage(_(u'msg_item_added',
                                     default=u'Added item to cart.'), 'info')
        else:
            ptool.addPortalMessage(_(u'msg_item_disabled',
                                     default=u'Item is disabled and can\'t be added.'), 'error')

        # redirect to referer
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        if referer == 'localhost':
            referer = context.absolute_url()
        self.request.response.redirect(referer)

    def _remove_item(self, key):
        """Remove the item with the given key from the cart.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, {})

        if key in cart_items:
            del cart_items[key]

        session[CART_KEY] = cart_items

    def remove_item(self):
        """Remove an item from cart.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')
        # remove_item doesn't expect skuCode but item keys - rename!
        skuCode = self.request.get('skuCode')
        if skuCode:
            self._remove_item(skuCode)
            ptool.addPortalMessage(_(u'msg_cart_updated',
                                     default=u"Cart updated."), 'info')

        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return

    def purge_cart(self):
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

    def update_cart(self):
        """Update cart contents.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')

        # first delete items with quantity 0
        del_items = []
        # XXX - these are not skuCodes but item keys - rename!
        for skuCode in self.get_items().keys():
            try:
                qty = int(float(self.request.get('quantity_%s' % skuCode)))
                if qty == 0:
                    del_items.append(skuCode)
            except (ValueError, TypeError):
                ptool.addPortalMessage(
                    _(u'msg_cart_invalidvalue',
                      default=u"Invalid Values specified. Cart not updated."),
                    'error')
                referer = self.request.get('HTTP_REFERER',
                                           context.absolute_url())
                self.request.response.redirect(referer)
                return
        for skuCode in del_items:
            self._remove_item(skuCode)

        # now update quantities (and VAT amounts, done by update_item)
        for skuCode, item in self.get_items().items():
            quantity = int(float(self.request.get('quantity_%s' % skuCode)))
            if quantity != item['quantity'] and quantity != 0:
                self.update_item(skuCode, quantity)

        ptool.addPortalMessage(_(u'msg_cart_updated',
                                 default=u"Cart updated."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)
        return


class CartView(BrowserView):
    """Shopping Cart related helper view that takes care of tasks not done by
    the IShoppingCart adapter.

    For backwards compatibility, this view wraps many of the methods of said
    adapter for now, but will eventually be phased out.
    """

    portlet_template = ViewPageTemplateFile('../portlets/cart.pt')

    @property
    def cart(self):
        if not hasattr(self, '_cart'):
            self._cart = getMultiAdapter((self.context, self.request),
                                         IShoppingCart)
        return self._cart

    def addtocart_ajax(self, skuCode=None, quantity=1,
                       var1choice=None, var2choice=None):
        """ Add item to cart, return portlet HTML and translated status
        message
        """
        translate = self.context.translate

        success = self.cart._add_item(skuCode, quantity, var1choice, var2choice)
        if success:
            status_msg_label = _(u'msg_label_info', default=u"Information")
            status_msg_text = _(u'msg_item_added', default=u"Added item to cart.")
        else:
            status_msg_label = _(u'msg_label_error', default=u"Error")
            status_msg_text = _(u'msg_item_disabled', default=u"Item is disabled and can't be added.")

        status_message = """\
<dt>%s</dt>
<dd>%s</dd>""" % (translate(status_msg_label),
               translate(status_msg_text))

        self.request.response.setHeader('Content-Type', 'application/json')
        return simplejson.dumps(dict(portlet_html=self.portlet_template(),
                    status_message=status_message))

    def addtocart(self, skuCode=None, quantity=1,
                  var1choice=None, var2choice=None):
        """Add item to cart and redirect to referer.

        The item must be identified by either its skuCode if it is an item
        without variations, or by its variation key.
        """
        return self.cart.add_item(skuCode=skuCode, quantity=quantity,
                                  var1choice=var1choice, var2choice=var2choice)

    def cart_items(self):
        """Get all items currently contained in shopping cart
        """
        return self.cart.get_items()

    def show_prices(self):
        return self.cart.get_show_prices()

    def cart_total(self):
        """Return the cart's total as a string
        """
        return self.cart.get_total()

    def cart_vat(self):
        """Return the cart's total VAT as a string
        """
        return self.cart.get_vat()

    def update_item(self, key, quantity):
        """Update the quantity of an item.
        """
        return self.cart.update_item(key, quantity)

    def cart_update(self):
        """Update cart contents.
        """
        return self.cart.update_cart()

    def cart_remove(self):
        """Remove an item from cart.
        """
        return self.cart.remove_item()

    def cart_delete(self):
        """Remove all items from cart.
        """
        return self.cart.purge_cart()


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
        navroot = api.portal.get_navigation_root(context)
        omanager = getMultiAdapter((navroot, self.request),
                                   name=u'order_manager')


        # Check we got all the data we need from the wizard
        try:
            order_id = omanager.addOrder()
        except MissingCustomerInformation:
            self.request.response.redirect('%s/checkout-wizard' % url)
            return
        except MissingShippingAddress:
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
        for name, adapter in getAdapters((context, context.REQUEST, context),
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

            omanager.sendOrderMails(order_id)

            self.request.response.redirect(
                        '%s/thankyou?order_id=%s' % (url, order.title))
            return
        else:
            #self.request.SESSION.invalidate()
            self.request.SESSION['order_id'] = order_id
            pp_launch_page = 'external-payment-processor'
            pp_launch_page = payment_processor.launch_page
            self.request.response.redirect('%s/%s' % (url, pp_launch_page))
            return

    def shop_config(self):
        """Return the shop configuration stored in the registry
        """
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        return shop_config
