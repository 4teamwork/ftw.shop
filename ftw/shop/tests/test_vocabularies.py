import unittest
from zope.schema.vocabulary import SimpleTerm

from ftw.shop.tests.base import FtwShopTestCase
from ftw.shop.vocabularies import create_terms_from_adapters
from ftw.shop.vocabularies import ContactInfoStepGroups
from ftw.shop.vocabularies import OrderReviewStepGroups
from ftw.shop.vocabularies import PaymentProcessorStepGroups
from ftw.shop.vocabularies import PaymentProcessors
from ftw.shop.vocabularies import EnabledPaymentProcessors
from ftw.shop.vocabularies import OrderStorageVocabulary

class TestVocabularies(FtwShopTestCase):
    
    def afterSetUp(self):
        super(TestVocabularies, self).afterSetUp()

    def test_create_terms_from_adapters(self):
        
        def mock_adapter_generator(n):
            
            class MockAdapter(object):
                pass
            
            for i in range(n):
                mock_adapter = MockAdapter()
                mock_adapter.title = "Adapter Title %s" % i
                yield ("adapter_name_%s" % i, mock_adapter)
    
        mock_adapters = mock_adapter_generator(3)            
        terms = create_terms_from_adapters(mock_adapters)
        expected_terms = [SimpleTerm(value="adapter_name_0", 
                                     token="adapter_name_0", 
                                     title="Adapter Title 0"),
                          SimpleTerm(value="adapter_name_1", 
                                     token="adapter_name_1", 
                                     title="Adapter Title 1"),
                          SimpleTerm(value="adapter_name_2", 
                                     token="adapter_name_2", 
                                     title="Adapter Title 2")]

        for i, term in enumerate(terms):
            self.assertEquals(term.value, expected_terms[i].value)
            self.assertEquals(term.token, expected_terms[i].token)
            self.assertEquals(term.title, expected_terms[i].title)

    def test_contact_info_step_groups(self):
        vocabulary = ContactInfoStepGroups(self.portal)
        self.assertEquals(vocabulary._terms[0].value,
                          u'ftw.shop.DefaultContactInformationStepGroup')
        self.assertEquals(vocabulary._terms[0].token,
                          u'ftw.shop.DefaultContactInformationStepGroup')
        self.assertEquals(vocabulary._terms[0].title,
                          u'title_default_contact_info_step_group')

    def test_order_review_step_groups(self):
        vocabulary = OrderReviewStepGroups(self.portal)
        self.assertEquals(vocabulary._terms[0].value,
                          u'ftw.shop.DefaultOrderReviewStepGroup')
        self.assertEquals(vocabulary._terms[0].token,
                          u'ftw.shop.DefaultOrderReviewStepGroup')
        self.assertEquals(vocabulary._terms[0].title,
                          u'title_default_order_review_step_group')

    def test_payment_processor_step_groups(self):
        vocabulary = PaymentProcessorStepGroups(self.portal)
        self.assertEquals(vocabulary._terms[0].value,
                          u'ftw.shop.DefaultPaymentProcessorStepGroup')
        self.assertEquals(vocabulary._terms[0].token,
                          u'ftw.shop.DefaultPaymentProcessorStepGroup')
        self.assertEquals(vocabulary._terms[0].title,
                          u'title_default_payment_processor_step_group')

    def test_payment_processors(self):
        vocabulary = PaymentProcessors(self.portal)
        self.assertTrue(u'ftw.shop.InvoicePaymentProcessor' in
                        [v for v in [t.value for t in vocabulary._terms]])

    def test_enabled_payment_processors(self):
        vocabulary = EnabledPaymentProcessors(self.portal)
        self.assertEquals(len(vocabulary), 1)
        self.assertEquals(vocabulary._terms[0].value,
                          u'ftw.shop.InvoicePaymentProcessor')
        self.assertEquals(vocabulary._terms[0].token,
                          u'ftw.shop.InvoicePaymentProcessor')
        self.assertEquals(vocabulary._terms[0].title,
                          'Gegen Rechnung')

    def test_order_storage_vocabulary(self):
        vocabulary = OrderStorageVocabulary(self.portal)
        self.assertEquals(vocabulary._terms[0].value,
                          u'ftw.shop.BTreeOrderStorage')
        self.assertEquals(vocabulary._terms[0].token,
                          u'ftw.shop.BTreeOrderStorage')
        self.assertEquals(vocabulary._terms[0].title,
                          u'BTree Storage')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestVocabularies))
    return suite
