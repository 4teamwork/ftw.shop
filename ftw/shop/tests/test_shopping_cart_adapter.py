from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.browser.cart import ShoppingCartAdapter
from ftw.shop.testing import FTW_SHOP_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase


class TestBrowserCart(TestCase):

    layer = FTW_SHOP_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        portal.REQUEST.set('SESSION', {})
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        self.supplier = create(Builder('supplier')
                               .titled('Demo Supplier')
                               .having(email='demo@email.com'))
        self.category = create(Builder('shop category').titled('Category'))
        self.subcategory = create(Builder('shop category')
                                  .within(self.category)
                                  .titled('SubCategory'))
        self.shopitem = create(Builder('shop item').within(self.subcategory))

    def test_get_supplier_from_shopitem(self):
        cart = ShoppingCartAdapter(self.shopitem, self.shopitem.REQUEST)
        cart.add_item()

        self.shopitem.setSupplier(IUUID(self.supplier))
        self.assertEquals(self.supplier, cart._get_supplier(self.shopitem))

    def test_get_supplier_from_parent(self):
        cart = ShoppingCartAdapter(self.shopitem, self.shopitem.REQUEST)
        cart.add_item()

        self.subcategory.setSupplier(IUUID(self.supplier))
        self.assertEquals(self.supplier, cart._get_supplier(self.shopitem))

    def test_get_supplier_recursively(self):
        cart = ShoppingCartAdapter(self.shopitem, self.shopitem.REQUEST)
        cart.add_item()

        self.category.setSupplier(IUUID(self.supplier))
        self.assertEquals(self.supplier, cart._get_supplier(self.shopitem))
