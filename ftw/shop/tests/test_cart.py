from decimal import Decimal
from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.config import SESSION_SHIPPING_KEY
from ftw.shop.interfaces import IShoppingCart
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
        cart.addtocart("12345", quantity=2, dimension=[Decimal(1), Decimal(2)])
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 1)
        item_key = self.movie.UID() + '==1-2'
        self.assertEquals(cart_items[item_key]['price'], '7.15')
        self.assertEquals(cart_items[item_key]['price_per_item'], '14.30')
        self.assertEquals(cart_items[item_key]['total'], '28.60')
        self.assertEquals(cart_items[item_key]['skucode'], '12345')
        self.assertEquals(cart_items[item_key]['quantity'], 2)
        self.assertEquals(cart_items[item_key]['title'], 'A Movie')
        self.assertEquals(cart_items[item_key]['description'], 'A Shop Item with no variations')
        self.assertEquals(cart.cart_total(), '28.60')

        # Add an item type that's already in the cart
        cart.addtocart("12345", quantity=1, dimension=[Decimal(1), Decimal(2)])
        self.assertEquals(cart.cart_items()[item_key]['quantity'], 3)
        self.assertEquals(cart.cart_total(), '42.90')


        # Add an item with one variation to cart
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Paperback', quantity=3)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 2)
        item_key = "%s=var-Paperback=" % self.book.UID()

        self.assertEquals(cart_items[item_key]['price'], '2.00')
        self.assertEquals(cart_items[item_key]['price_per_item'], '2.00')
        self.assertEquals(cart_items[item_key]['total'], '6.00')
        self.assertEquals(cart_items[item_key]['skucode'], 'b22')
        self.assertEquals(cart_items[item_key]['quantity'], 3)
        self.assertEquals(cart_items[item_key]['title'], 'Professional Plone Development - None')
        self.assertEquals(cart_items[item_key]['description'], 'A Shop Item with one variation')

        self.assertEquals(cart.cart_total(), '48.90')

        # Add an item type with variations that's already in the cart
        cart.addtocart(var1choice='Paperback', quantity=1)
        self.assertEquals(cart.cart_items()[item_key]['quantity'], 4)
        self.assertEquals(cart.cart_total(), '50.90')


        # Add an item with two variations to cart
        cart = getMultiAdapter((self.tshirt, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Green', var2choice='M', quantity=4)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 3)
        item_key = "%s=var-Green-M=" % self.tshirt.UID()
        self.assertEquals(cart_items[item_key]['price'], '5.00')
        self.assertEquals(cart_items[item_key]['price_per_item'], '5.00')
        self.assertEquals(cart_items[item_key]['total'], '20.00')
        self.assertEquals(cart_items[item_key]['skucode'], '55')
        self.assertEquals(cart_items[item_key]['quantity'], 4)
        self.assertEquals(cart_items[item_key]['title'], 'A T-Shirt - None')
        self.assertEquals(cart_items[item_key]['description'], 'A Shop Item with two variations')

        self.assertEquals(cart.cart_total(), '70.90')
        cart.cart_delete()

    def test_add_with_different_and_same_dimensions(self):
        # Add an item with dimensions
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart("12345", quantity=1, dimension=[Decimal(1), Decimal(2)])
        cart_items = cart.cart_items()
        item_key = self.movie.UID() + '==1-2'

        self.assertEquals(1, len(cart_items))

        # adding with same dimensions does not add a second item in the cart
        cart.addtocart("12345", quantity=2, dimension=[Decimal(1), Decimal(2)])
        cart_items = cart.cart_items()
        self.assertEquals(1, len(cart_items))
        self.assertEquals(3, cart_items[item_key]['quantity'])

        # adding with different dimensions adds a second item
        cart.addtocart("12345", quantity=1, dimension=[Decimal(3), Decimal(3)])
        cart_items = cart.cart_items()
        self.assertEquals(2, len(cart_items))

        cart.cart_delete()

    def test_add_to_cart_ajax(self):
        # Add an item with no variations to cart
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart_response = cart.addtocart_ajax("12345", quantity=2, dimensions='1|2')
        cart_response_dict = simplejson.loads(cart_response)
        portlet_html = cart_response_dict['portlet_html']
        status_message = cart_response_dict['status_message']
        self.assertEquals(status_message, "<dt>Information</dt>\n<dd>Added item to cart.</dd>")
        self.assertTrue('<dl class="portlet portletCartPortlet">' in portlet_html)
        self.assertTrue('28.60' in portlet_html)
        self.assertTrue('(2)' in portlet_html)
        self.assertTrue('<div class="cartTotal">Total: CHF 28.60</div>' in portlet_html)
        self.assertEquals(cart.cart_total(), '28.60')
        cart.cart_delete()

    def test_remove_item(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart_item_count = len(cart.cart_items())
        cart.addtocart(skuCode='12345', dimension=[Decimal(1), Decimal(2)])
        movie_key = self.movie.UID()+'==1-2'
        self.assertEquals(len(cart.cart_items()), cart_item_count + 1)
        self.assertTrue(movie_key in cart.cart_items())
        cart.cart._remove_item(movie_key)
        self.assertEquals(len(cart.cart_items()), cart_item_count)
        self.assertTrue(movie_key not in cart.cart_items())

    def test_update_item(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1, dimension=[Decimal(1), Decimal(2)])
        movie_key = self.movie.UID()+'==1-2'
        cart.update_item(movie_key, 2, [2, 2])
        movie_key = self.movie.UID() + '==2-2'
        self.assertEquals(cart.cart_items()[movie_key]['quantity'], 2)
        self.assertEquals(cart.cart_items()[movie_key]['price_per_item'], '28.60')
        self.assertEquals(cart.cart_items()[movie_key]['total'], '57.20')

    def test_cart_update(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1, dimension=[Decimal(1), Decimal(2)])
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='b11', var1choice='Hardcover', quantity=2)

        # Try to update cart with no values in request (invalid)
        cart.cart_update()
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Invalid Values specified. Cart not updated.')
        self.assertEquals(len(cart.cart_items()), 2)

        # Modify quantities
        self.portal.REQUEST['quantity_%s==1-2' % self.movie.UID()] = 2
        self.portal.REQUEST['dimension_%s==1-2' % self.movie.UID()] = [1, 2]
        self.portal.REQUEST['quantity_%s=var-Hardcover=' % self.book.UID()] = 0
        cart.cart_update()
        self.assertEquals(cart.cart_items()[self.movie.UID()+'==1-2']['quantity'], 2)
        self.assertTrue('b11' not in cart.cart_items())
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Cart updated.')

    def test_cart_item_order(self):
        # Previously the order of the items was random. This test failed about
        # half the times it was run. The OrderedDict change fixed it.
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='b11', var1choice='Hardcover', quantity=2)
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1, dimension=[Decimal(1), Decimal(2)])
        cart.cart_update()
        self.assertEquals(
            ['b11', '12345'],
            [item['skucode'] for item in cart.cart_items().values()])

    def test_changing_dimensions_updates_key(self):
        # Add an item with dimensions
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart("12345", quantity=1, dimension=[Decimal(1), Decimal(2)])
        cart_items = cart.cart_items()

        self.assertEquals(1, len(cart_items))

        # updating the dimensions will change the key
        self.portal.REQUEST['dimension_%s==1-2' % self.movie.UID()] = [3, 3]
        self.portal.REQUEST['quantity_%s==1-2' % self.movie.UID()] = 1
        cart.cart_update()

        self.assertEquals([self.movie.UID()+'==3-3'], cart.cart_items().keys())

        # add a second item and change it to the same dimensions
        # as the first item
        cart.addtocart("12345", quantity=2, dimension=[Decimal(1), Decimal(2)])

        self.assertEquals(2, len(cart.cart_items()))

        self.portal.REQUEST['dimension_%s==1-2' % self.movie.UID()] = [3, 3]
        self.portal.REQUEST['quantity_%s==1-2' % self.movie.UID()] = 2
        self.portal.REQUEST['dimension_%s==3-3' % self.movie.UID()] = [3, 3]
        self.portal.REQUEST['quantity_%s==3-3' % self.movie.UID()] = 1
        cart.cart_update()

        ptool = getToolByName(self.portal, 'plone_utils')
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Invalid Values specified. Cart not updated.')

        cart_items = cart.cart_items()
        self.assertEquals(2, len(cart_items))
        self.assertEquals(1, cart_items[self.movie.UID()+'==3-3']['quantity'])

    def test_cart_remove(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart('12345', dimension=[Decimal(1), Decimal(2)])

        # Remove the item we just added
        item_key = self.movie.UID() + '==1-2'
        # XXX - this is not an skuCode but an item key - rename!
        self.portal.REQUEST['skuCode'] = item_key
        cart.cart_remove()
        self.assertEquals(len(cart.cart_items()), 0)
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u"Cart updated.")

    def test_cart_delete(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart('12345', dimension=[Decimal(1), Decimal(2)])
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
        cart.addtocart('12345', dimension=[Decimal(1), Decimal(2)])
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
        self.assertEquals(order.total, Decimal('14.30'))
        self.assertEquals(order.status, 3)
        self.assertEquals(order.customer_firstname, "Hugo")
        self.assertEquals(order.customer_lastname, "Boss")
        self.assertEquals(order.customer_email, "hugo.boss@example.org")

    def test_calc_item_total(self):
        cart = getMultiAdapter((self.portal, self.portal.REQUEST), IShoppingCart)
        self.assertEqual(
            7.5,
            cart.calc_item_total(7.5, 1, [1], 1),
            "Price should be respected in the calculation")
        self.assertEqual(
            15,
            cart.calc_item_total(7.5, 2, [1], 1),
            "Quantity should be respected in the calculation")
        self.assertEqual(
            15,
            cart.calc_item_total(7.5, 1, [2], 1),
            "Dimension should be respected in the calculation")
        self.assertEqual(
            60,
            cart.calc_item_total(7.5, 1, [2, 2, 2], 1),
            "Multiple dimensions should be respected in the calculation")
        self.assertEqual(
            120,
            cart.calc_item_total(7.5, 2, [2, 2, 2], 1),
            "Quantity and dimensions can be used simultaneously")
        self.assertEqual(
            4.4,
            float(cart.calc_item_total(11, 2, [0.2, 1, 1], 1)),
            "Decimal dimensions should be respected in the calculation.")
        self.assertEqual(
            2.2,
            # 11.-/m2 and 10mm * 1000mm dimensions
            float(cart.calc_item_total(11, 2, [100, 1000], 1000000)),
            "The price modifier is used to convert price unit to dimension unit.")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCart))
    return suite
