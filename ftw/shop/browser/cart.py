from Acquisition import aq_inner, aq_parent
from collections import OrderedDict
from decimal import Decimal
from decimal import getcontext
from decimal import InvalidOperation
from decimal import ROUND_UP
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

        # Setup Decimal environment
        getcontext().rounding = ROUND_UP

    @property
    def catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = getToolByName(self.context, 'portal_catalog')
        return self._catalog

    def get_item_key(self, uid, variation_code, dimensions=None):
        """A unique id for each item / variation / dimension combination.
        """
        dimcode = '-'.join([str(dim) for dim in dimensions]) if dimensions else ''

        return '='.join([uid, variation_code, dimcode])

    def get_items(self):
        """Get all items currently contained in shopping cart
        """
        # Avoid creating a session if there doesn't exist one yet.
        bid_manager = getToolByName(self.context, 'browser_id_manager')
        browser_id = bid_manager.getBrowserId(create=0)
        if not browser_id:
            return {}
        session = self.request.SESSION
        items = session.get(CART_KEY, OrderedDict())
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
        return '{:.2f}'.format(total)

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
                # Strip of variation suffix from itemkey to get the uid.
                variation_suffix = itemvalue['variation_code'].strip('var')
                uid = itemkey[:-len(variation_suffix)]
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

    def calc_item_total(self, price, quantity, dimensions, price_modifier):
        # calculates the item total form price, dimensions and quantity
        # the dimensions_modifier is needed because the price is sometimes in a
        # different unit than the dimensions (amount in g, price in kg)
        return quantity * self.calc_price_per_item(price, dimensions, price_modifier)

    def calc_price_per_item(self, price, dimensions, price_modifier):
        size = reduce(lambda x, y: x * y, dimensions) if dimensions else 1
        return Decimal(size) * Decimal(price) / Decimal(price_modifier)

    def calc_vat(self, rate, total):
        """Calculate VAT and round to correct precision.
        """
        vat_amount = (Decimal(rate) / 100) * total
        vat_amount = vat_amount.quantize(Decimal('.01'))
        return vat_amount

    def has_single_supplier(self):
        """Returns true if all the suppliers are the same, or there are no
        suppliers whatsoever.
        """
        suppliers = self.get_suppliers()
        return all(x == suppliers[0] for x in suppliers)

    def has_specified_dimensions(self):
        """Checks if any item has dimensions.
        """
        for item in self.get_items().values():
            if len(item['dimensions']) > 0:
                return True
        return False

    def update_item(self, key, quantity, dimensions):
        """Update the quantity or dimensions of an item.
        """
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, OrderedDict())

        if key not in cart_items:
            return

        item = cart_items[key]
        item['quantity'] = int(quantity)
        item['dimensions'] = dimensions
        price_per_item = self.calc_price_per_item(Decimal(item['price']),
                                                  dimensions,
                                                  item['price_modifier'])
        total = self.calc_item_total(Decimal(item['price']),
                                     item['quantity'],
                                     dimensions,
                                     item['price_modifier'])
        item['price_per_item'] = '{:.2f}'.format(price_per_item)
        item['total'] = '{:.2f}'.format(total)
        item['vat_amount'] = str(self.calc_vat(item['vat_rate'], total))
        cart_items[key] = item

        # update the key if the dimensions changed
        new_key = self.get_item_key(
            item['uid'],
            item['variation_code'] if 'variation_code' in item else '',
            dimensions)
        if key != new_key:
            cart_items[new_key] = cart_items[key]
            del cart_items[key]

        session[CART_KEY] = cart_items

    def _add_item(self, skuCode=None, quantity=1,
                   var1choice=None, var2choice=None, dimensions=None):
        """ Add item to cart
        """
        context = aq_inner(self.context)
        varConf = IVariationConfig(self.context)

        # get current items in cart
        session = self.request.SESSION
        cart_items = session.get(CART_KEY, OrderedDict())
        variation_code = varConf.variation_code(var1choice, var2choice)

        # We got no skuCode, so look it up by variation key
        if not skuCode:
            skuCode = varConf.sku_code(var1choice, var2choice)

        item_key = self.get_item_key(self.context.UID(), variation_code, dimensions)
        item = cart_items.get(item_key, None)

        item_title = context.Title()
        quantity = int(quantity)
        vat_rate = Decimal(context.getField('vat').get(context))

        supplier_name, supplier_email = self._get_supplier_info(context)

        if dimensions is None:
            dimensions = []

        price_modifier = self.context.getPriceModifier()

        has_variations = varConf.hasVariations()
        if has_variations:
            variation_dict = varConf.getVariationDict()
            if not variation_dict[variation_code]['active']:
                # Item is disabled
                return False

            variation_pretty_name = varConf.getPrettyName(variation_code)
            item_title = '%s - %s' % (context.Title(), variation_pretty_name)
            price = Decimal(variation_dict[variation_code]['price'])

            price_per_item = self.calc_price_per_item(price, dimensions, price_modifier)

            # add item to cart
            if item is None:
                total = self.calc_item_total(price, quantity, dimensions, price_modifier)

                item = {'uid': self.context.UID(),
                        'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'show_price': context.showPrice,
                        'total': '{:.2f}'.format(total),
                        'price_per_item': '{:.2f}'.format(price_per_item),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                        'variation_code': variation_code,
                        'vat_rate': vat_rate,
                        'vat_amount': str(self.calc_vat(vat_rate, total)),
                        'dimensions': dimensions,
                        'selectable_dimensions': context.getSelectableDimensions(),
                        'price_modifier': price_modifier
                }
            # item already in cart, update quantity
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                total = self.calc_item_total(price, item['quantity'], dimensions, price_modifier)
                item['dimensions'] = dimensions
                item['total'] = '{:.2f}'.format(total)
                item['price_per_item'] = '{:.2f}'.format(price_per_item)
                item['vat_amount'] = str(self.calc_vat(vat_rate, total))

        else:
            price = Decimal(context.Schema().getField('price').get(context))
            price_per_item = self.calc_price_per_item(price, dimensions, price_modifier)

            # add item to cart
            if item is None:
                total = self.calc_item_total(price, quantity, dimensions, price_modifier)
                item = {'uid': self.context.UID(),
                        'title': item_title,
                        'description': context.Description(),
                        'skucode': skuCode,
                        'quantity': quantity,
                        'price': str(price),
                        'show_price': context.showPrice,
                        'total': '{:.2f}'.format(total),
                        'price_per_item': '{:.2f}'.format(price_per_item),
                        'url': context.absolute_url(),
                        'supplier_name': supplier_name,
                        'supplier_email': supplier_email,
                        'vat_rate': vat_rate,
                        'vat_amount': str(self.calc_vat(vat_rate, total)),
                        'dimensions': dimensions,
                        'selectable_dimensions': context.getSelectableDimensions(),
                        'price_modifier': price_modifier
                }
            # item already in cart, update quantity
            else:
                item['quantity'] = item.get('quantity', 0) + quantity
                total = self.calc_item_total(price, item['quantity'], dimensions, price_modifier)
                item['dimensions'] = dimensions
                item['total'] = '{:.2f}'.format(total)
                item['price_per_item'] = '{:.2f}'.format(price_per_item)
                item['vat_amount'] = str(self.calc_vat(vat_rate, total))

        # store cart in session
        cart_items[item_key] = item
        session[CART_KEY] = cart_items
        return True

    def add_item(self, skuCode=None, quantity=1,
                 var1choice=None, var2choice=None, dimensions=None):
        """Add item to cart and redirect to referer.

        The item must be identified by either its skuCode if it is an item
        without variations, or by its variation key.
        """
        context = aq_inner(self.context)
        ptool = getToolByName(context, 'plone_utils')

        # Add item to cart
        success = self._add_item(skuCode, quantity, var1choice, var2choice, dimensions)
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
        cart_items = session.get(CART_KEY, OrderedDict())

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
        session[CART_KEY] = OrderedDict()

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

        # delete items with quantity 0
        del_items = []
        for item_key in self.get_items().keys():
            try:
                qty = int(float(self.request.get('quantity_%s' % item_key)))
                if qty <= 0:
                    del_items.append(item_key)
            except (ValueError, TypeError):
                ptool.addPortalMessage(
                    _(u'msg_cart_invalidvalue',
                      default=u"Invalid Values specified. Cart not updated."),
                    'error')
                referer = self.request.get('HTTP_REFERER',
                                           context.absolute_url())
                self.request.response.redirect(referer)
                return
        for item_key in del_items:
            self._remove_item(item_key)

        # now update quantities and dimensions
        for item_key, item in self.get_items().items():
            quantity = float(self.request.get('quantity_%s' % item_key))

            dimensions = self.request.get('dimension_%s' % item_key, [])
            if not isinstance(dimensions, list):
                dimensions = [dimensions]

            if not validate_dimensions(dimensions, item['selectable_dimensions']):
                ptool.addPortalMessage(
                    _(u'msg_cart_invalidvalue',
                      default=u"Invalid Values specified. Cart not updated."),
                    'error')
                referer = self.request.get('HTTP_REFERER',
                                           context.absolute_url())
                self.request.response.redirect(referer)
                return

            dimensions = map(Decimal, dimensions)

            # check that dimension changes do not collide
            item = self.get_items()[item_key]
            new_key = self.get_item_key(
                item['uid'],
                item['variation_code'] if 'variation_code' in item else '',
                dimensions)
            if new_key != item_key and new_key in self.get_items().keys():
                ptool.addPortalMessage(
                    _(u'msg_cart_invalidvalue',
                      default=u"Invalid Values specified. Cart not updated."),
                    'error')
                referer = self.request.get('HTTP_REFERER',
                                           context.absolute_url())
                self.request.response.redirect(referer)
                return

            self.update_item(item_key, quantity, dimensions)

        ptool.addPortalMessage(_(u'msg_cart_updated',
                                 default=u"Cart updated."), 'info')
        referer = self.request.get('HTTP_REFERER', context.absolute_url())
        self.request.response.redirect(referer)


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
                       var1choice=None, var2choice=None, dimensions=None):
        """ Add item to cart, return portlet HTML and translated status
        message
        """
        translate = self.context.translate

        # unpack dimensions from request
        dimensions = dimensions.split('|') if dimensions else []

        if validate_dimensions(dimensions, self.context.getSelectableDimensions()):
            dimensions = map(Decimal, dimensions)

            success = self.cart._add_item(skuCode, quantity, var1choice, var2choice, dimensions)

            if success:
                status_msg_label = _(u'msg_label_info', default=u"Information")
                status_msg_text = _(u'msg_item_added', default=u"Added item to cart.")
            else:
                status_msg_label = _(u'msg_label_error', default=u"Error")
                status_msg_text = _(u'msg_item_disabled', default=u"Item is disabled and can't be added.")

        else:
            status_msg_label = _(u'msg_label_error', default=u"Error")
            status_msg_text = _(u'msg_invalid_dimensions', default=u"Invalid dimensions.")

        status_message = """\
<dt>%s</dt>
<dd>%s</dd>""" % (translate(status_msg_label),
               translate(status_msg_text))

        self.request.response.setHeader('Content-Type', 'application/json')
        return simplejson.dumps(dict(portlet_html=self.portlet_template(),
                    status_message=status_message))

    def addtocart(self, skuCode=None, quantity=1,
                  var1choice=None, var2choice=None, dimension=None):
        """Add item to cart and redirect to referer.

        The item must be identified by either its skuCode if it is an item
        without variations, or by its variation key.
        """
        # wrap single dimension in list so all dimensions are lists
        if not dimension:
            dimension = []
        if not isinstance(dimension, list):
            dimension = [dimension]

        if not validate_dimensions(dimension, self.context.getSelectableDimensions()):
            raise ValueError('Invalid dimensions.')

        dimension = map(Decimal, dimension)
        return self.cart.add_item(skuCode=skuCode, quantity=quantity,
                                  var1choice=var1choice, var2choice=var2choice,
                                  dimensions=dimension)

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

    def update_item(self, key, quantity, dimensions):
        """Update the quantity of an item.
        """
        return self.cart.update_item(key, quantity, dimensions)

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

    def cart_has_dimensions(self):
        """Checks if any item has dimensions.
        """
        return self.cart.has_specified_dimensions()

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


def validate_dimensions(dimensions, selectable_dimensions):
    """ Checks if the request has the sane amount of dimensions. """
    if dimensions is None or selectable_dimensions is None:
        return False

    if len(dimensions) != len(selectable_dimensions):
        return False

    try:
        dimensions = map(Decimal, dimensions)
    except InvalidOperation:
        return False

    for dimension in dimensions:
        if dimension <= 0:
            return False

    return True
