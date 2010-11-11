from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.component import getAdapters, getUtility, getUtilitiesFor
from zope.interface import directlyProvides
from plone.registry.interfaces import IRegistry

from ftw.shop.interfaces import IContactInformationStepGroup
from ftw.shop.interfaces import IOrderReviewStepGroup
from ftw.shop.interfaces import IPaymentProcessorStepGroup
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IShopConfiguration



def create_terms_from_adapters(adapters):
    """Returns a list of terms to be used to create a vocabulary,
    including a nice human readable title if defined for the adapter
    """
    adapter_names = []
    adapter_titles = []
    items = []
    for name, adapter in adapters:
        adapter_names.append(unicode(name))
        title = getattr(adapter, 'title', name)
        adapter_titles.append(title)

    for i in range(0, len(adapter_names)):
        items.append(tuple([adapter_names[i], adapter_titles[i]]))

    terms = [SimpleTerm(value=pair[0],
            token=pair[0],
            title=pair[1]) for pair in items]
    return terms

def ContactInfoStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    contact information StepGroup
    """
    # context is the portal config options, whose context is the portal
    contact_info_step_groups = getAdapters((context, None, context),
                                     IContactInformationStepGroup)
    terms = create_terms_from_adapters(contact_info_step_groups)

    directlyProvides(ContactInfoStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)

def OrderReviewStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    order review StepGroup
    """
    # context is the portal config options, whose context is the portal
    order_review_step_groups = getAdapters((context, None, context),
                                     IOrderReviewStepGroup)
    terms = create_terms_from_adapters(order_review_step_groups)

    directlyProvides(OrderReviewStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)

def PaymentProcessorStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    payment processor StepGroup
    """
    # context is the portal config options, whose context is the portal
    payment_processor_step_groups = getAdapters((context, None, context),
                                     IPaymentProcessorStepGroup)
    terms = create_terms_from_adapters(payment_processor_step_groups)

    directlyProvides(PaymentProcessorStepGroups, IVocabularyFactory)

    return vocabulary.SimpleVocabulary(terms)


def PaymentProcessors(context):
    """Returns a vocabulary of the registered PaymentProcessors
    """
    # context is the portal config options, whose context is the portal
    payment_processors = getAdapters((context, None, context),
                                     IPaymentProcessor)
    terms = create_terms_from_adapters(payment_processors)

    directlyProvides(PaymentProcessors, IVocabularyFactory)

    return vocabulary.SimpleVocabulary(terms)


def EnabledPaymentProcessors(context):
    """Returns a vocabulary of the PaymentProcessors that have been enabled
    in the shop configuration.
    """
    # context is the portal config options, whose context is the portal
    registry = getUtility(IRegistry)
    shop_config = registry.forInterface(IShopConfiguration)
    payment_processors = getAdapters((context, None, context),
                                     IPaymentProcessor)
    terms = create_terms_from_adapters(payment_processors)
    for term in terms:
        if term.value not in shop_config.enabled_payment_processors:
            terms.remove(term)

    directlyProvides(EnabledPaymentProcessors, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def OrderStorageVocabulary(context):
    """Returns a vocabulary of the currently registered utilities 
    that implement IOrderStorage.
    """
    # context is the portal config options, whose context is the portal
    order_storages = getUtilitiesFor(IOrderStorage)
    terms = create_terms_from_adapters(order_storages)

    directlyProvides(OrderStorageVocabulary, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)
