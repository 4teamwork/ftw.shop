from ftw.shop import shopMessageFactory as _
from plone.theme.interfaces import IDefaultPloneLayer
from zope import schema
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class IShopRoot(Interface):
    """Marker interface for shop root folder."""

class IBuyable(Interface):
    """Marker interface for marking items as buyable."""

class IShopItem(Interface):
    """A simple shop item"""
    

class IVariationConfig(Interface):
    """A component which provides variation configurations.
    """
    def getVariations(self):
        """Returns the variations stored on a ShopItem. 
        """
        
class IFtwShopSpecific(IDefaultPloneLayer):
    """Marker interface for a zope 3 browser layer.
    """

class IShopListing(IViewletManager):
    """ Viewlet manager registration for shop view
    """

class IShopCompactListing(IViewletManager):
    """ Compact Viewlet manager registration for shop view
    """

class IShopOrder(Interface):
    """A shop order"""
    

class IShopCategory(Interface):
    """A category for shop items"""
    
# ------------------------------------------------------

class IWizardStep(Interface):
    """A wizard step"""
    
class IWizardStepGroup(Interface):
    """A wizard step"""
    
class IPaymentProcessor(Interface):
    """A payment processor"""

class IContactInformationStepGroup(IWizardStepGroup):
    """A wizard step group gathering contact information about the customer"""

class IContactInformationStep(IWizardStep):
    """A wizard step gathering contact information about the customer"""
    
    
    
class IPaymentProcessorChoiceStep(IWizardStep):
    """A wizard step asking to choose a payment processor"""
    
class IPaymentProcessorDetailsStep(IWizardStep):
    """A wizard step asking for details regarding the payment processor"""
    
class IPaymentProcessorStepGroup(IWizardStepGroup):
    """A wizard step group gathering contact information about the payment processor"""
    

class IOrderReviewStep(IWizardStep):
    """A wizard step asking the customer to review the order and payment
    details and confirm the order."""



# ------------------------------------------------------


class IShopConfiguration(Interface):
    """This interface defines the ftw.shop configlet."""

    shop_name = schema.TextLine(
            title=_(u"label_shop_name", default=u"Enter the shop name"),
            required=True)

    enabled_payment_processors = schema.List(
            title=_(u"label_enabled_payment_processors", 
                    default="Enabled Payment Processors"),
            value_type=schema.Choice(vocabulary="ftw.shop.payment_processors"),)

    contact_info_step_group = schema.Choice(
            title=_(u"label_contact_info_step_group", 
                    default="Contact Information Step Group"),
            vocabulary="ftw.shop.contact_info_step_groups",
            required=True)
    

class IDefaultPaymentProcessorChoice(Interface):
    """Schema defining a choice from available payment processors
    """
    payment_processor = schema.Choice(
            title=_(u"label_payment_processor", default="Payment Processor"),
            vocabulary="ftw.shop.enabled_payment_processors",
            required=True)
    
class IDefaultPaymentProcessorDetails(Interface):
    """Schema defining details for a chosen payment processor
    """
    details = schema.TextLine(
            title=_(u"label_payment_processor_details", 
                    default="Payment Processor Details"),
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

    street = schema.TextLine(
            title=_(u'label_street', default=u'Street/No.'),
            required=True)

    street2 = schema.TextLine(
            title=_(u'label_street2', default=u'Address 2'),
            required=False)

    phone = schema.TextLine(
            title=_(u'label_phone_number', default=u'Phone number'),
            required=True)

    zipcode = schema.Int(
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
