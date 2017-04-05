from ftw.shop import shopMessageFactory as _
from ftw.shop.config import DEFAULT_VAT_RATES
from ftw.shop.utils import is_email_valid
from plone.theme.interfaces import IDefaultPloneLayer
from z3c.form import validator
from z3c.form.interfaces import IRadioWidget
from z3c.form.validator import SimpleFieldValidator
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid


class IShopRoot(Interface):
    """DEPRECATED!
    Former marker interface for shop root folder.
    """


class IBuyable(Interface):
    """Marker interface for marking items as buyable.
    """


class IShopItem(Interface):
    """A simple shop item
    """


class IShopCategory(Interface):
    """A category for shop items
    """


class IVariationConfig(Interface):
    """A component which provides variation configurations.
    """

    def getVariations(self):
        """Returns the variations stored on a ShopItem.
        """


class IShopOrder(Interface):
    """A shop order
    """


class ICartItem(Interface):
    """A shop item that has been added to the cart and is part of an order
    """


class IMailHostAdapter(Interface):
    """Adapter to abstract Plone 3 and Plone 4 MailHosts
    """

    def send(self, msg_body, mto, mfrom=None, mbcc=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        """Abstract sending mail with Plone 3 and Plone 4.
        """


# ------------ Storage related interfaces -------------

class IOrderStorage(Interface):
    """A local utility which stores the shop orders
    """

    def createOrder(self):
        pass

    def getOrder(self, order_id):
        pass

    def flush(self):
        pass



# ------------ Checkout Wizard related interfaces -------------

class IWizardStep(Interface):
    """A wizard step
    """


class IWizardStepGroup(Interface):
    """A wizard step group
    """


class IPaymentProcessor(Interface):
    """A payment processor
    """


class IContactInformationStepGroup(IWizardStepGroup):
    """A wizard step group gathering contact information about the customer
    """


class IContactInformationStep(IWizardStep):
    """A wizard step gathering contact information about the customer
    """


class IShippingAddressStepGroup(IWizardStepGroup):
    """A wizard step group gathering contact information about the
    preferred shipping address.
    """


class IShippingAddressStep(IWizardStep):
    """A wizard step gathering contact information about the preferred
    shipping address.
    """


class IPaymentProcessorChoiceStep(IWizardStep):
    """A wizard step asking to choose a payment processor
    """


class IDefaultPaymentProcessorChoice(Interface):
    """Schema defining a customer choice from enabled payment processors
    """
    payment_processor = schema.Choice(
            title=_(u"label_payment_processor", default="Payment Processor"),
            vocabulary="ftw.shop.enabled_payment_processors",
            required=True)


class IPaymentProcessorWidget(IRadioWidget):
    """Radio widget with fancy labels.
    """


class IPaymentProcessorStepGroup(IWizardStepGroup):
    """A wizard step group gathering contact information about the payment
    processor
    """


class IOrderReviewStep(IWizardStep):
    """A wizard step asking the customer to review the order and payment
    details and confirm the order.
    """


class IOrderReviewStepGroup(IWizardStepGroup):
    """A wizard step group for the order review step(s)
    """

# ------------------ Configuration Schemata -----------------------------

class IShopConfiguration(Interface):
    """This interface defines the ftw.shop configlet.
    """

    shop_name = schema.TextLine(
            title=_(u"label_shop_name", default=u"Enter the shop name"),
            required=True,
            default=u"Webshop")

    shop_email = schema.TextLine(
            title=_(u"label_shop_email", default=u"Sender e-Mail Address"),
            required=True,
            default=u"webshop@example.org")

    mail_bcc = schema.TextLine(
            title=_(u"label_mail_bcc", default=u"BCC Address"),
            required=False,
            default=u"")

    mail_subject = schema.TextLine(
            title=_(u"label_mail_subject",
                    default=u"Subject"),
            description=_(u"help_mail_subject",
                    default=u"The subject for order mails."),
            required=False,
            default=u"")

    phone_number = schema.TextLine(
        title=_(u'label_phone_number',
                default=u'Phone number'),
        description=_(u'help_phone_number',
                      default=u'Will be displayed in the customer confirmation mail'
                      ' as contact information when configured.'),
        required=False,
        default=u'')

    always_notify_shop_owner = schema.Bool(
            title=_(u"label_always_notify_shop_owner",
                    default=u"Always notify shop owner about orders"),
            description=_(u"help_always_notify_shop_owner",
                    default=u"Also send eMail to owner if supplier(s) have "
                             "been notified"),
            required=False)

    payment_processor_step_group = schema.Choice(
            title=_(u"label_payment_processor_step_group",
                    default="Payment Processor Step Group"),
            vocabulary="ftw.shop.payment_processor_step_groups",
            default=u"ftw.shop.DefaultPaymentProcessorStepGroup",
            required=True)

    enabled_payment_processors = schema.List(
            title=_(u"label_enabled_payment_processors",
                    default="Enabled Payment Processors"),
            required=False,
            default=[u'ftw.shop.InvoicePaymentProcessor'],
            value_type=schema.Choice(
                            vocabulary="ftw.shop.payment_processors"),
                            )

    order_storage = schema.Choice(
            title=_(u"label_order_storage",
                    default="Order Storage method"),
            required=True,
            default=u'ftw.shop.BTreeOrderStorage',
            vocabulary="ftw.shop.order_storage_vocabulary")

    contact_info_step_group = schema.Choice(
            title=_(u"label_contact_info_step_group",
                    default="Contact Information Step Group"),
            vocabulary="ftw.shop.contact_info_step_groups",
            default=u"ftw.shop.DefaultContactInformationStepGroup",
            required=True)

    shipping_address_step_group = schema.Choice(
            title=_(u"label_shipping_address_step_group",
                    default="Shipping Address Step Group"),
            vocabulary="ftw.shop.shipping_address_step_groups",
            default=u"ftw.shop.DefaultShippingAddressStepGroup",
            required=True)

    order_review_step_group = schema.Choice(
            title=_(u"label_order_review_step_group",
                    default="Order Review Step Group"),
            vocabulary="ftw.shop.order_review_step_groups",
            default=u"ftw.shop.DefaultOrderReviewStepGroup",
            required=True)

    status_set = schema.Choice(
            title=_(u"label_status_set",
                    default="Status Set"),
            vocabulary="ftw.shop.status_sets_vocabulary",
            default=u'ftw.shop.DefaultStatusSet',
            required=True)

    show_status_column = schema.Bool(
            title=_(u"label_show_status_column",
                    default=u"Show status column in order manager"),
            description=_(u"help_show_status_column",
                    default=u""),
            default=True,
            required=False)

    vat_enabled = schema.Bool(
            title=_(u"label_vat_enabled",
                    default=u"Enable VAT support"),
            description=_(u"help_vat_enabled",
                    default=u""),
            default=True,
            required=False)

    vat_number = schema.TextLine(
            title=_(u"label_vat_number",
                    default=u"VAT number"),
            description=_(u"help_vat_number",
                    default=u""),
            default=u'',
            required=False)

    vat_rates = schema.List(
            title=_(u"label_vat_rates",
                    default=u"VAT rates"),
            description=_(u"help_vat_rates",
                    default=u""),
            value_type=schema.Decimal(),
            default=DEFAULT_VAT_RATES,
            required=False)


class IDefaultContactInformation(Interface):
    """Schema defining a common contact address form
    """
    title= schema.TextLine(
            title=_(u'label_title', default=u'Title'),
            required=True)

    firstname = schema.TextLine(
            title=_(u'label_firstname', default=u'First Name'),
            required=True)

    lastname = schema.TextLine(
            title=_(u'label_lastname', default=u'Last Name'),
            required=True)

    email = schema.TextLine(
            title=_(u'label_email', default=u'Email'),
            required=True)

    company = schema.TextLine(
            title=_(u'label_company', default=u'Company'),
            required=False)

    street1 = schema.TextLine(
            title=_(u'label_street', default=u'Street/No.'),
            required=True)

    street2 = schema.TextLine(
            title=_(u'label_street2', default=u'Address 2'),
            required=False)

    phone = schema.TextLine(
            title=_(u'label_phone_number', default=u'Phone number'),
            required=True)

    zipcode = schema.TextLine(
            title=_(u'label_zipcode', default=u'Zip Code'),
            required=True)

    city = schema.TextLine(
            title=_(u'label_city', default=u'City'),
            required=True)

    country = schema.TextLine(
            title=_(u'label_country', default=u'Country'),
            required=True)


class IOrderReviewSchema(Interface):
    """Fields for the order review step.
    """

    comments = schema.Text(
            title=_(u'label_comments', default=u'Comments'),
            required=False)


class EmailAddressValidator(SimpleFieldValidator):

    def validate(self, value):
        super(EmailAddressValidator, self).validate(value)
        if not value or not is_email_valid(value):
            raise Invalid(_(u'This email address is invalid.'))


validator.WidgetValidatorDiscriminators(
    EmailAddressValidator,
    field=IDefaultContactInformation['email'])


class IShippingAddress(Interface):
    """Schema defining a form for entering a shipping address
    """

    used = schema.Bool(
            title=_(u'label_used', default=u'Different from invoice address'),
            default=False,
            required=False)

class IStatusSet(Interface):
    """Interface defining a set of statuses that an order can
    be in.
    """


class ISupplier(Interface):
    """A supplier
    """


class IFtwShopSpecific(IDefaultPloneLayer):
    """Marker interface for a zope 3 browser layer.
    """


class IShoppingCart(Interface):
    """ShoppingCart adapter
    """
