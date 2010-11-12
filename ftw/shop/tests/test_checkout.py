import unittest
import simplejson
import base64

from ftw.shop.browser.checkout import CheckoutView
from ftw.shop.browser.checkout import CheckoutWizard
from ftw.shop.browser.checkout import DefaultContactInfoStep
from ftw.shop.browser.cart import CartView
from ftw.shop.config import SESSION_ADDRESS_KEY, COOKIE_ADDRESS_KEY
from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.tests.base import MOCK_CUSTOMER


class TestCheckout(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestCheckout, self).afterSetUp()
        self.checkout_view = CheckoutView(self.portal, self.portal.REQUEST)
        self.wizard = CheckoutWizard(self.portal, self.portal.REQUEST)
 
    def test_checkout_view(self):
        self.assertTrue(isinstance(self.checkout_view, CheckoutView))
        self.assertTrue(isinstance(self.portal.REQUEST['cart_view'], CartView))

    def test_wizard_steps(self):
        wizard = self.wizard
        steps = wizard.steps
        default_contact_info_step = steps[0]
        default_payment_processor_choice_step = steps[1]
        default_order_review_step = steps[2]
        
        self.assertEquals(default_contact_info_step.title, 
                          u'title_default_contact_info_step')
        self.assertEquals(default_payment_processor_choice_step.title, 
                          u'title_default_payment_processor_step')
        self.assertEquals(default_order_review_step.title, 
                          u'title_default_order_review_step')
        
    def test_default_contact_info_step(self):
        wizard = self.wizard
        session = self.portal.REQUEST.SESSION

        # Test form prefill from data in session
        session[SESSION_ADDRESS_KEY] = MOCK_CUSTOMER

        step = DefaultContactInfoStep(self.portal, 
                                      self.portal.REQUEST,
                                      wizard)
        for key in MOCK_CUSTOMER.keys():
            self.assertEquals(step.fields[key].field.default,
                              MOCK_CUSTOMER[key])
            
        
        # Test form prefill from cookie
        cookie_data = base64.b64encode(simplejson.dumps(MOCK_CUSTOMER))
        self.portal.REQUEST[COOKIE_ADDRESS_KEY] = cookie_data
        step = DefaultContactInfoStep(self.portal, 
                                      self.portal.REQUEST,
                                      wizard)
        for key in MOCK_CUSTOMER.keys():
            self.assertEquals(step.fields[key].field.default,
                              MOCK_CUSTOMER[key])




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCheckout))
    return suite
