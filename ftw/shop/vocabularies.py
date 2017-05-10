from ftw.shop import shopMessageFactory as _
from ftw.shop.content.shopitem import selectable_dimensions
from ftw.shop.interfaces import IContactInformationStepGroup
from ftw.shop.interfaces import IOrderReviewStepGroup
from ftw.shop.interfaces import IOrderStorage
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IPaymentProcessorStepGroup
from ftw.shop.interfaces import IShippingAddressStepGroup
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IStatusSet
from functools import partial
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapters, getUtility, getUtilitiesFor
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import directlyProvides
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm


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

    items.sort()
    terms = [SimpleTerm(value=pair[0],
                        token=pair[0],
                        title=pair[1]) for pair in items]
    return terms


def ContactInfoStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    contact information StepGroup
    """
    request = getSite().REQUEST
    # context is the portal config options, whose context is the portal
    contact_info_step_groups = getAdapters((context, request, context),
                                           IContactInformationStepGroup)
    terms = create_terms_from_adapters(contact_info_step_groups)

    directlyProvides(ContactInfoStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def ShippingAddressStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    shipping address StepGroup
    """
    # context is the portal config options, whose context is the portal
    request = getSite().REQUEST
    shipping_address_step_groups = getAdapters((context, request, context),
                                               IShippingAddressStepGroup)
    terms = create_terms_from_adapters(shipping_address_step_groups)

    directlyProvides(ShippingAddressStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def OrderReviewStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    order review StepGroup
    """
    # context is the portal config options, whose context is the portal
    request = getSite().REQUEST
    order_review_step_groups = getAdapters((context, request, context),
                                           IOrderReviewStepGroup)
    terms = create_terms_from_adapters(order_review_step_groups)

    directlyProvides(OrderReviewStepGroups, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def PaymentProcessorStepGroups(context):
    """Returns a vocabulary of the registered StepGroups for the
    payment processor StepGroup
    """
    # context is the portal config options, whose context is the portal
    request = getSite().REQUEST
    payment_processor_step_groups = getAdapters((context, request, context),
                                                IPaymentProcessorStepGroup)
    terms = create_terms_from_adapters(payment_processor_step_groups)

    directlyProvides(PaymentProcessorStepGroups, IVocabularyFactory)

    return vocabulary.SimpleVocabulary(terms)


def PaymentProcessors(context):
    """Returns a vocabulary of the registered PaymentProcessors
    """
    # context is the portal config options, whose context is the portal
    request = getSite().REQUEST
    payment_processors = getAdapters((context, request, context),
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
    request = getSite().REQUEST
    payment_processors = getAdapters((context, request, context),
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


def StatusSetsVocabulary(context):
    """Returns a vocabulary of the currently registered utilities
    that implement IStatusSet.
    """
    # context is the portal config options, whose context is the portal
    status_sets = getAdapters((context,), IStatusSet)
    terms = create_terms_from_adapters(status_sets)

    directlyProvides(StatusSetsVocabulary, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def VATRatesVocabulary(context):
    """Returns a vocabulary of the VAT rates that are available
    to choose from.
    """
    # context is the portal config options, whose context is the portal
    registry = getUtility(IRegistry)
    shop_config = registry.forInterface(IShopConfiguration)
    vat_rates = shop_config.vat_rates

    terms = [SimpleTerm(value=str(rate), token=rate, title=str(rate))
             for rate in vat_rates]

    directlyProvides(VATRatesVocabulary, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def SuppliersVocabulary(context):
    """Returns a vocabulary of the available suppliers
    """
    # context is the portal config options, whose context is the portal
    catalog = getToolByName(context, 'portal_catalog')
    suppliers = catalog(portal_type="Supplier")
    items = [(brain.UID, brain.Title) for brain in suppliers]
    terms = [SimpleTerm(value=pair[0],
                        token=pair[0],
                        title=pair[1]) for pair in items]
    terms.insert(0, SimpleTerm(value='',
                               token='none',
                               title=_("label_supplier_from_parent",
                                       default="Supplier from parent category")))

    directlyProvides(SuppliersVocabulary, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)


def SelectableDimensionsVocabulary(context):
    """Returns a vocabulary of the available suppliers
    """
    transl = partial(translate, context=context.REQUEST)

    terms = []
    for key, value in selectable_dimensions.iteritems():
        title = transl(value['label'])
        if key != 'no_dimensions':
            form = transl(_(
                u'dimensions_format',
                default=u'%(label)s (%(dimension)s) - price in %(price)s',
            ))
            title = form % {
                'label': title,
                'dimension': transl(value['dimension_unit']),
                'price': transl(value['price_unit'] if 'price_unit' in value else translate(value['dimension_unit']))
            }

        terms.append(SimpleTerm(value=key, token=key, title=title))

    terms = sorted(terms, key=lambda term: term.title)

    directlyProvides(SelectableDimensionsVocabulary, IVocabularyFactory)
    return vocabulary.SimpleVocabulary(terms)
