from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.component import getAdapters, getUtility, getUtilitiesFor
from zope.interface import directlyProvides
from plone.registry.interfaces import IRegistry

from ftw.shop.interfaces import IContactInformationStepGroup
from ftw.shop.interfaces import IOrderReviewStepGroup
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IShopConfiguration


def ContactInfoStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    contact information StepGroup
    """
    # context is the portal config options, whose context is the portal
    contact_info_step_groups = getAdapters((context, None, context),
                                           IContactInformationStepGroup)

    step_names = set(map(unicode, [n for n, a in contact_info_step_groups]))
    directlyProvides(ContactInfoStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(step_names)

def OrderReviewStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    order review StepGroup
    """
    # context is the portal config options, whose context is the portal
    order_review_step_groups = getAdapters((context, None, context),
                                           IOrderReviewStepGroup)

    step_names = set(map(unicode, [n for n, a in order_review_step_groups]))
    directlyProvides(OrderReviewStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary.fromValues(step_names)


def PaymentProcessors(context):
    """Returns a vocabulary of the registered PaymentProcessors
    """
    # context is the portal config options, whose context is the portal
    payment_processors = getAdapters((context, None, context),
                                     IPaymentProcessor)
    processor_names = []
    processor_titles = []
    items = []

    for n, a in payment_processors:
        processor_names.append(unicode(n))
        processor_titles.append(a.title)

    for i in range(0, len(processor_names)):
        items.append(tuple([processor_names[i], processor_titles[i]]))

    terms = [SimpleTerm(value=pair[0],
                         token=pair[0],
                         title=pair[1]) for pair in items]

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
    processor_names = []
    processor_titles = []
    items = []

    for n, a in payment_processors:
        processor_names.append(unicode(n))
        processor_titles.append(a.title)

    for i in range(0, len(processor_names)):
        if processor_names[i] in shop_config.enabled_payment_processors:
            items.append(tuple([processor_names[i], processor_titles[i]]))

    terms = [SimpleTerm(value=pair[0],
                         token=pair[0],
                         title=pair[1]) for pair in items]

    directlyProvides(EnabledPaymentProcessors, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def OrderStorageVocabulary(context):
    """Returns a vocabulary of the currently registered utilities 
    that implement IOrderStorage.
    """
    # context is the portal config options, whose context is the portal
    order_storages = getUtilitiesFor(IOrderStorage)
    storage_names = []
    storage_titles = []
    items = []

    for n, a in order_storages:
        storage_names.append(unicode(n))
        storage_titles.append(a.title)

    for i in range(0, len(storage_names)):
        items.append(tuple([storage_names[i], storage_titles[i]]))

    terms = [SimpleTerm(value=pair[0],
                         token=pair[0],
                         title=pair[1]) for pair in items]

    directlyProvides(OrderStorageVocabulary, IVocabularyFactory)

    return vocabulary.SimpleVocabulary(terms)
