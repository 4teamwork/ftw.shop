from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getAdapters, getUtility
from zope.interface import directlyProvides
from plone.registry.interfaces import IRegistry

from ftw.shop.interfaces import IContactInformationStepGroup
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IShopConfiguration

def ContactInfoStepGroups(context):
    # context is the portal config options, whose context is the portal
    contact_info_step_groups = getAdapters((context, None, context,), IContactInformationStepGroup)
    step_names = set( map(unicode, [ n for n,a in contact_info_step_groups]) )
    directlyProvides(ContactInfoStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(step_names)

def PaymentProcessors(context):
    # context is the portal config options, whose context is the portal
    payment_processors = getAdapters((context, None, context,), IPaymentProcessor)
    processor_names = set( map(unicode, [ n for n,a in payment_processors]) )
    directlyProvides(PaymentProcessors, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(processor_names)

def EnabledPaymentProcessors(context):
    # context is the portal config options, whose context is the portal
    payment_processors = getAdapters((context, None, context,), IPaymentProcessor)
    registry = getUtility(IRegistry)
    shop_config = registry.forInterface(IShopConfiguration)
    processor_names = set( map(unicode, [ n for n,a in payment_processors]) )
    enabled_processor_names = [pn for pn in processor_names 
                               if pn in shop_config.enabled_payment_processors]
    directlyProvides(EnabledPaymentProcessors, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(enabled_processor_names)
