import unittest
from Products.CMFCore.utils import getToolByName
import zope.event
from Products.Archetypes.event import ObjectInitializedEvent
from ftw.shop.tests.base import FtwShopTestCase


class TestSetup(FtwShopTestCase):
    
    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        self.setRoles(('Manager',))
        self.portal.invokeFactory("ShopCategory", "shop")
        self.setRoles(('Member',))

    def test_add_shop_type_permissisons(self):
        # The API of the permissionsOfRole() function sucks - it is bound too
        # closely up in the permission management screen's user interface
        roles = ['Manager', 'Contributor']
        for r in roles:
            selected_permissions = [p['name'] for p in 
                                    self.portal.permissionsOfRole(r) if p['selected']]
            self.failUnless('ftw.shop: Add Shop Item' in selected_permissions)
            self.failUnless('ftw.shop: Add Shop Category' in selected_permissions)
            if r == 'Manager':
                self.failUnless('ftw.shop: Add Order' in selected_permissions)

            
    def test_shop_types_installed(self):
        self.failUnless('ShopCategory' in self.types.objectIds())
        self.failUnless('ShopItem' in self.types.objectIds())
        
    def test_shop_category_fti(self):
        document_fti = getattr(self.types, 'ShopCategory')
        self.failUnless(document_fti.global_allow)
        self.failUnless('ShopCategory' in document_fti.allowed_content_types)
        self.failUnless('ShopItem' in document_fti.allowed_content_types)

    def test_shop_item_creation(self):
        self.setRoles(('Manager',))
        self.portal.shop.invokeFactory('ShopItem', 'test-item')
        self.setRoles(('Member',))
        self.failUnless(self.portal.shop['test-item'].id == 'test-item')

    def test_shop_item_default_category(self):
        self.setRoles(('Manager',))
        self.portal.shop.invokeFactory('ShopItem', 'test-item')
        item = self.portal.shop['test-item']
        self.setRoles(('Member',))

        event = ObjectInitializedEvent(item, self.portal.REQUEST)
        zope.event.notify(event)
        
        self.failUnless(self.portal.shop in item.listCategories())


        





def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
