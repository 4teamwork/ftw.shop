import unittest
import simplejson

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from ftw.shop.config import SESSION_ADDRESS_KEY
from ftw.shop.tests.base import FtwShopTestCase


class TestCart(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestCart, self).afterSetUp()

    def test_add_to_cart(self):
        # Add an item with no variations to cart
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart("12345", quantity=2)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 1)
        self.assertEquals(cart_items['12345']['price'], '7.15')
        self.assertEquals(cart_items['12345']['total'], '14.30')
        self.assertEquals(cart_items['12345']['skucode'], '12345')
        self.assertEquals(cart_items['12345']['quantity'], 2)
        self.assertEquals(cart_items['12345']['title'], 'A Movie')
        self.assertEquals(cart_items['12345']['description'], 'A Shop Item with no variations')
        
        self.assertEquals(cart.cart_total(), '14.30')
        
        # Add an item type that's already in the cart
        cart.addtocart("12345", quantity=1)
        self.assertEquals(cart.cart_items()['12345']['quantity'], 3)
        self.assertEquals(cart.cart_total(), '21.45')
        

        # Add an item with one variation to cart
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Paperback', quantity=3)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 2)
        self.assertEquals(cart_items['b22']['price'], '2.00')
        self.assertEquals(cart_items['b22']['total'], '6.00')
        self.assertEquals(cart_items['b22']['skucode'], 'b22')
        self.assertEquals(cart_items['b22']['quantity'], 3)
        self.assertEquals(cart_items['b22']['title'], 'Professional Plone Development - Paperback')
        self.assertEquals(cart_items['b22']['description'], 'A Shop Item with one variation')
        
        self.assertEquals(cart.cart_total(), '27.45')

        # Add an item type with variations that's already in the cart
        cart.addtocart(var1choice='Paperback', quantity=1)
        self.assertEquals(cart.cart_items()['b22']['quantity'], 4)
        self.assertEquals(cart.cart_total(), '29.45')
        

        # Add an item with two variations to cart
        cart = getMultiAdapter((self.tshirt, self.portal.REQUEST), name='cart_view')
        cart.addtocart(var1choice='Green', var2choice='M', quantity=4)
        cart_items = cart.cart_items()
        self.assertEquals(len(cart_items), 3)
        self.assertEquals(cart_items['55']['price'], '5.00')
        self.assertEquals(cart_items['55']['total'], '20.00')
        self.assertEquals(cart_items['55']['skucode'], '55')
        self.assertEquals(cart_items['55']['quantity'], 4)
        self.assertEquals(cart_items['55']['title'], 'A T-Shirt - Green-M')
        self.assertEquals(cart_items['55']['description'], 'A Shop Item with two variations')
        
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
        self.assertTrue('12345' in cart.cart_items())
        cart.remove_item('12345')
        self.assertEquals(len(cart.cart_items()), cart_item_count)
        self.assertTrue('12345' not in cart.cart_items())
        
    def test_update_item(self):
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1)
        cart.update_item('12345', 2)
        self.assertEquals(cart.cart_items()['12345']['quantity'], 2)
        self.assertEquals(cart.cart_items()['12345']['total'], '14.30')
        
    def test_cart_update(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='12345', quantity=1)
        cart = getMultiAdapter((self.book, self.portal.REQUEST), name='cart_view')
        cart.addtocart(skuCode='b11', quantity=2)
        
        # Try to update cart with no values in request (invalid)
        cart.cart_update()
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Invalid Values specified. Cart not updated.')
        self.assertEquals(len(cart.cart_items()), 2)
        
        # Modify quantities
        self.portal.REQUEST['quantity_12345'] = 2
        self.portal.REQUEST['quantity_b11'] = 0
        cart.cart_update()
        self.assertEquals(cart.cart_items()['12345']['quantity'], 2)
        self.assertTrue('b11' not in cart.cart_items())
        last_msg = ptool.showPortalMessages()[-1].message
        self.assertEquals(last_msg, u'Cart updated.')

    def test_cart_remove(self):
        ptool = getToolByName(self.portal, 'plone_utils')
        cart = getMultiAdapter((self.movie, self.portal.REQUEST), name='cart_view')
        cart.addtocart('12345')
        
        # Remove the item we just added
        self.portal.REQUEST['skuCode'] = '12345'
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
        omanager = getMultiAdapter((self.portal, self.portal.REQUEST), 
                                   name=u'order_manager')

        self.portal.REQUEST.SESSION[SESSION_ADDRESS_KEY] = customer_info
        self.portal.REQUEST.SESSION['order_confirmation'] = True
        self.portal.REQUEST.SESSION['payment_processor_choice'] = pp_choice
        cart.checkout()
        
        order = omanager.getOrders()[0]
        self.assertEquals(order.total, '7.15')
        self.assertEquals(order.status, 3)
        self.assertEquals(order.customer_firstname, "Hugo")
        self.assertEquals(order.customer_lastname, "Boss")      


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCart))
    return suite
