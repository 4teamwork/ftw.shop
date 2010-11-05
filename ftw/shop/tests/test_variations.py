import unittest
from decimal import Decimal
from Products.CMFCore.utils import getToolByName
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.interfaces import IVariationConfig


class TestVariations(FtwShopTestCase):
    
    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        self.setRoles(('Manager',))
        self.portal.invokeFactory("ShopCategory", "shop")
        self.portal.shop.invokeFactory('ShopItem', 't-shirt')
        self.item = self.portal.shop['t-shirt']
        
        self.item.getField('variation1_attribute').set(self.item, 'Color')
        self.item.getField('variation1_values').set(self.item, ['Red', 'Green', 'Blue'])
        self.item.getField('variation2_attribute').set(self.item, 'Size')
        self.item.getField('variation2_values').set(self.item, ['S', 'M', 'L', 'XL'])
        
        self.var_conf = IVariationConfig(self.item)
        
        var_dict = {
        'red-s': {'active': True, 'price': Decimal('1.00'), 'stock': 1, 'skuCode': '11'},
        'red-m': {'active': True, 'price': Decimal('2.00'), 'stock': 2, 'skuCode': '22'}, 
        'red-l': {'active': True, 'price': Decimal('3.00'), 'stock': 3, 'skuCode': '33'},
        'green-s': {'active': True, 'price': Decimal('4.00'), 'stock': 4, 'skuCode': '44'},
        'green-m': {'active': True, 'price': Decimal('5.00'), 'stock': 5, 'skuCode': '55'}, 
        'green-l': {'active': True, 'price': Decimal('6.00'), 'stock': 6, 'skuCode': '66'}, 
        'blue-s': {'active': True, 'price': Decimal('7.00'), 'stock': 7, 'skuCode': '77'}, 
        'blue-m': {'active': True, 'price': Decimal('8.00'), 'stock': 8, 'skuCode': '88'}, 
        'blue-l': {'active': True, 'price': Decimal('9.00'), 'stock': 9, 'skuCode': '99'},
        }
        
        self.var_conf.updateVariationConfig(var_dict)
        
        self.setRoles(('Member',))

    def test_has_variations(self):
        self.failUnless(self.var_conf.hasVariations())

    def test_get_item_uid(self):
        self.failUnless(self.var_conf.getItemUID() == self.item.UID())

    def test_get_var1_values(self):
        var1_values = self.var_conf.getVariation1Values()
        self.failUnless(var1_values == ('Red', 'Green', 'Blue'))

    def test_get_var2_values(self):
        var2_values = self.var_conf.getVariation2Values()
        self.failUnless(var2_values == ('S', 'M', 'L', 'XL'))

    def test_get_variation_attributes(self):
        var_attrs = self.var_conf.getVariationAttributes()
        self.failUnless(var_attrs == ['Color', 'Size'])

    def test_get_variation_data(self):
        price = self.var_conf.getVariationData('Blue', 'S', 'price')
        stock = self.var_conf.getVariationData('Blue', 'S', 'stock')
        skuCode = self.var_conf.getVariationData('Blue', 'S', 'skuCode')
        active = self.var_conf.getVariationData('Blue', 'S', 'active')
        self.failUnless(price == Decimal('7.00'))
        self.failUnless(stock == 7)
        self.failUnless(skuCode == '77')
        self.failUnless(active)
        
    def test_get_pretty_name(self):
        self.failUnless(self.var_conf.getPrettyName('blue-s') == 'Blue-S')
        
    def test_get_variation_dict(self):
        expected_var_dict = {
        'red-s': {'active': True, 'price': Decimal('1.00'), 'stock': 1, 'skuCode': '11'},
        'red-m': {'active': True, 'price': Decimal('2.00'), 'stock': 2, 'skuCode': '22'}, 
        'red-l': {'active': True, 'price': Decimal('3.00'), 'stock': 3, 'skuCode': '33'},
        'green-s': {'active': True, 'price': Decimal('4.00'), 'stock': 4, 'skuCode': '44'},
        'green-m': {'active': True, 'price': Decimal('5.00'), 'stock': 5, 'skuCode': '55'}, 
        'green-l': {'active': True, 'price': Decimal('6.00'), 'stock': 6, 'skuCode': '66'}, 
        'blue-s': {'active': True, 'price': Decimal('7.00'), 'stock': 7, 'skuCode': '77'}, 
        'blue-m': {'active': True, 'price': Decimal('8.00'), 'stock': 8, 'skuCode': '88'}, 
        'blue-l': {'active': True, 'price': Decimal('9.00'), 'stock': 9, 'skuCode': '99'},
        }
        self.failUnless(self.var_conf.getVariationDict() == expected_var_dict)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestVariations))
    return suite
