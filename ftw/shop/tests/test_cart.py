from decimal import Decimal
from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.config import SESSION_SHIPPING_KEY
from ftw.shop.tests.base import FtwShopTestCase
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import simplejson
import unittest


class TestCart(FtwShopTestCase):

    def afterSetUp(self):
        super(TestCart, self).afterSetUp()

    def test_add_to_cart(self):
        # Add an item with no variations to cart
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart("12345", quantity=2)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 1)
        item_uid = self.movie.UID()
        self.assertEquals(cart_items[item_uid]['price'], '7.15')
        self.assertEquals(cart_items[item_uid]['total'], '14.30')
        self.assertEquals(cart_items[item_uid]['skucode'], '12345')
        self.assertEquals(cart_items[item_uid]['quantity'], 2)
        self.assertEquals(cart_items[item_uid]['title'], 'A Movie')
        self.assertEquals(cart_items[item_uid]['description'], 'A Shop Item with no variations')

        self.assertEquals(cart.cart_total(), '14.30')

        # Add an item type that's already in the cart
        cart.addtocart("12345", quantity=1)
        self.assertEquals(cart.cart_items()[item_uid]['quantity'], 3)
        self.assertEquals(cart.cart_total(), '21.45')


        # Add an item with one variation to cart
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Paperback', quantity=3)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 2)
        item_uid = "%s-Paperback" % self.book.UID()

        self.assertEquals(cart_items[item_uid]['price'], '2.00')
        self.assertEquals(cart_items[item_uid]['total'], '6.00')
        self.assertEquals(cart_items[item_uid]['skucode'], 'b22')
        self.assertEquals(cart_items[item_uid]['quantity'], 3)
        self.assertEquals(cart_items[item_uid]['title'], 'Professional Plone Development - None')
        self.assertEquals(cart_items[item_uid]['description'], 'A Shop Item with one variation')

        self.assertEquals(cart.cart_total(), '27.45')

        # Add an item type with variations that's already in the cart
        cart.addtocart(var1choice='Paperback', quantity=1)
        self.assertEquals(cart.cart_items()[item_uid]['quantity'], 4)
        self.assertEquals(cart.cart_total(), '29.45')


        # Add an item with two variations to cart
        cart = getMultiAdapter((self.tshirt, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Green', var2choice='M', quantity=4)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 3)
        item_uid = "%s-Green-M" % self.tshirt.UID()
        self.assertEquals(cart_items[item_uid]['price'], '5.00')
        self.assertEquals(cart_items[item_uid]['total'], '20.00')
        self.assertEquals(cart_items[item_uid]['skucode'], '55')
        self.assertEquals(cart_items[item_uid]['quantity'], 4)
        self.assertEquals(cart_items[item_uid]['title'], 'A T-Shirt - None')
        self.assertEquals(cart_items[item_uid]['description'], 'A Shop Item with two variations')

        self.assertEquals(cart.cart_total(), '49.45')
        cart.cart_delete()

    def test_add_to_cart_ajax(self):
        # Add an item with no variations to cart
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart_response = cart.addtocart_ajax("12345", quantity=2)
        cart_response_dict = simplejson.loads(cart_response)
        portlet_html = cart_response_dict['portlet_html']
        status_message = cart_response_dict['status_message']
        self.assertEquals(status_message, "<dt>Information</dt>\n<dd>Added item to cart.</dd>")
        self.assertTrue('<dl class="portlet portletCartPortlet">' in portlet_html)
        self.assertTrue('14.30' in portlet_html)
        self.assertTrue('(2)' in portlet_html)
        self.assertTrue('<div class="cartTotal">Total: CHF 14.30</div>' in portlet_html)
        self.assertEquals(cart.cart_total(), '14.30')
        cart.cart_delete()

    def test_remove_item(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart_item_count = len(cart.cart_items())
        cart.addtocart(skuCode='12345')
        self.assertEquals(len(cart.cart_items()), cart_item_count + 1)
        self.assertTrue(self.movie.UID() in cart.cart_items())
        cart.cart._remove_item(self.movie.UID())
        self.assertEquals(len(cart.cart_items()), cart_item_count)
        self.assertTrue(self.movie.UID() not in cart.cart_items())

    def test_update_item(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1)
        cart.update_item(self.movie.UID(), 2)
        self.assertEquals(cart.cart_items()[self.movie.UID()]['quantity'], 2)
        self.assertEquals(cart.cart_items()[self.movie.UID()]['total'], '14.30')

    def test_cart_update(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1)
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='b11', var1choice='Hardcover', quantity=2)

        # Try to update cart with no values in request (invalid)
        cart.cart_update()
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Invalid Values specified. Cart not updated.')
        self.assertEquals(len(cart.cart_items()), 2)

        # Modify quantities
        self.portal.REQUEST['quantity_%s' % self.movie.UID()] = 2
        self.portal.REQUEST['quantity_%s-Hardcover' % self.book.UID()] = 0
        cart.cart_update()
        self.assertEquals(cart.cart_items()[self.movie.UID()]['quantity'], 2)
        self.assertTrue('b11' not in cart.cart_items())
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Cart updated.')

    def test_cart_remove(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart('12345')

        # Remove the item we just added
        item_key = self.movie.UID()
        # XXX - this is not an skuCode but an item key - rename!
        self.portal.REQUEST['skuCode'] = item_key
        cart.cart_remove()
        self.assertEquals(len(cart.cart_items()), 0)
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u"Cart updated.")

    def test_cart_delete(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart('12345')
        self.assertEquals(len(cart.cart_items()), 1)

        cart.cart_delete()
        self.assertEquals(len(cart.cart_items()), 0)

    def test_checkout(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        pp_choice = {'payment_processor': 'ftw.shop.InvoicePaymentProcessor'}
        customer_info = {'title': 'Mr.',
                         'firstname': "Hugo",
                         'lastname': "Boss",
                         'email': 'hugo.boss@example.org'}
        shipping_info = {'title': 'Mr.',
                         'firstname': "Hugo",
                         'lastname': "Boss"}
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')

        # Test checkout with empty cart
        cart.checkout()
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u"Can't proceed with empty cart.")

        # Test checkout with item in cart but missing order confirmation
        cart.addtocart('12345')
        self.portal.REQUEST.SESSION[SESSION_ADDRESS_KEY] = customer_info
        cart.checkout()

        # Test checkout with item in cart but missing payment processor
        self.portal.REQUEST.SESSION[SESSION_ADDRESS_KEY] = customer_info
        self.portal.REQUEST.SESSION['order_confirmation'] = True
        cart.checkout()

        # Test checkout with item and all necessary information
        navroot = api.portal.get_navigation_root(self.movie)
        omanager = getMultiAdapter((navroot, self.portal.REQUEST),
                                   name=u'order_manager')

        self.portal.REQUEST.SESSION[SESSION_ADDRESS_KEY] = customer_info
        self.portal.REQUEST.SESSION[SESSION_SHIPPING_KEY] = shipping_info
        self.portal.REQUEST.SESSION['order_confirmation'] = True
        self.portal.REQUEST.SESSION['payment_processor_choice'] = pp_choice
        cart.checkout()

        order = omanager.getOrders()[0]
        self.assertEquals(order.total, Decimal('7.15'))
        self.assertEquals(order.status, 3)
        self.assertEquals(order.customer_firstname, "Hugo")
        self.assertEquals(order.customer_lastname, "Boss")
        self.assertEquals(order.customer_email, "hugo.boss@example.org")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCart))
    return suite
