from plone.theme.interfaces import IDefaultPloneLayer
from zope import schema
from zope.interface import Interface
from z3c.form.interfaces import IRadioWidget

from ftw.shop import shopMessageFactory as _


class IShopRoot(Interface):
    """Marker interface for shop root folder.
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

    def getAllOrders(self):
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

    mail_subject_de = schema.TextLine(
            title=_(u"label_mail_subject_de",
                    default=u"Order Mail Subject (Deutsch)"),
            required=False,
            default=u"")

    mail_subject_en = schema.TextLine(
            title=_(u"label_mail_subject_en",
                    default=u"Order Mail Subject (English)"),
            required=False,
            default=u"")

    shop_phone = schema.TextLine(
            title=_(u"label_shop_phone",
                    default=u"Shop Phone Number"),
            required=False)

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
            vocabulary="ftw.shop.order_storage_vocabulary"
            )

    contact_info_step_group = schema.Choice(
            title=_(u"label_contact_info_step_group",
                    default="Contact Information Step Group"),
            vocabulary="ftw.shop.contact_info_step_groups",
            required=True)


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

    newsletter = schema.Bool(
            title=_(u'label_newsletter', default=u'Newsletter'),
            description=_(u'help_newsletter',
                    default=u'I would like to subscribe to the newsletter.'),
            required=False,
            default=False)

    comments = schema.Text(
            title=_(u'label_comments', default=u'Comments'),
            required=False)


class IFtwShopSpecific(IDefaultPloneLayer):
    """Marker interface for a zope 3 browser layer.
    """
