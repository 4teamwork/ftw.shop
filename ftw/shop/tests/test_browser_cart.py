from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.tests.pages import cartportlet
from ftw.shop.tests.pages import shopitem
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
import transaction


class TestBrowserCart(TestCase):

    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        create(Builder('cart portlet'))
        transaction.commit()

    @browsing
    def test_adding_items_to_cart(self, browser):
        browser.login().open()
        self.assertTrue(cartportlet.is_visible(), 'Cart portlet should be visible.')
        self.assertTrue(cartportlet.is_empty(), 'Cart portlet should be empty.')

        item = create(Builder('shop item')
                      .titled('A pair of socks'))
        browser.visit(item)
        shopitem.add_to_cart()
        self.assertEquals(['A pair of socks'], cartportlet.items())

    @browsing
    def test_edit_cart_link_visible_when_cart_has_items(self, browser):
        browser.login().open()
        self.assertFalse(cartportlet.edit_cart_link(),
                         '"Edit cart" link should not be visible yet.')

        item = create(Builder('shop item'))
        browser.visit(item)
        shopitem.add_to_cart()
        self.assertTrue(cartportlet.edit_cart_link(),
                        '"Edit cart" link should now be visible.')

    @browsing
    def test_edit_cart_link_opens_edit_cart_view(self, browser):
        item = create(Builder('shop item'))
        browser.login().visit(item)
        shopitem.add_to_cart()
        cartportlet.edit_cart_link().click()
        self.assertEquals('cart_edit', plone.view())

    @browsing
    def test_order_link_opens_checkout_wizard(self, browser):
        item = create(Builder('shop item'))
        browser.login().visit(item)
        shopitem.add_to_cart()
        cartportlet.order_link().click()
        self.assertEquals('checkout-wizard', plone.view())

    @browsing
    def test_order_manager_link_visible_for_superuser(self, browser):
        browser.login().open()
        self.assertTrue(
            cartportlet.order_manager_link(),
            'The test user (Manager) should see the "Order Manager" link.')

    @browsing
    def test_order_manager_link_invisible_for_normal_user(self, browser):
        normal_user = create(Builder('user'))
        browser.login(normal_user.getId()).open()
        self.assertFalse(
            cartportlet.order_manager_link(),
            'The normal user (Member) should NOT see the "Order Manager" link.')

    @browsing
    def test_order_manager_link_points_to_order_manager_view(self, browser):
        browser.login().open()
        cartportlet.order_manager_link().click()
        self.assertEquals('order_manager', plone.view())
