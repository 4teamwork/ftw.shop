from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.schema.vocabulary import SimpleVocabulary

from zope import schema, interface

from ftw.shop import shopMessageFactory as _


class IShopRoot(Interface):
    """Marker interface for shop root folder."""

class IBuyable(Interface):
    """Marker interface for marking items as buyable."""

class IVariationConfig(Interface):
    """A component which provides variation configurations.
    """
    def getVariations():
        """Returns the variations stored on a ShopItem. 
        """

class IFtwShopSpecific(IDefaultPloneLayer):
    """Marker interface for a zope 3 browser layer.
    """

class IShopListing(IViewletManager):
    """ Viewlet manager registration for shop view
    """



class ICustomerInformation(Interface):
    
    # id = schema.TextLine(
    #     title=u'ID',
    #     readonly=True,
    #     required=True)

    title= schema.TextLine(
        title=u'Title',
        required=True)

    firstname = schema.TextLine(
        title=u'First Name',
        required=True)

    lastname = schema.TextLine(
        title=u'Last Name',
        required=True)

    email = schema.TextLine(
        title=u'Email',
        required=True)

    street = schema.TextLine(
        title=u'Street/No.',
        required=True)

    street2 = schema.TextLine(
        title=u'Address 2',
        required=False)

    phone = schema.TextLine(
        title=u'Phone number',
        required=True)

    zipcode = schema.Int(
        title=u'Zip Code',
        required=True)

    city = schema.TextLine(
        title=u'City',
        required=True)

    newsletter = schema.Bool(
        title=u'Newsletter',
        description=u'I would like to subscribe to the newsletter.',
        required=False,
        default=False)

    comments = schema.Text(
        title=u'Comments',
        required=False)


    # @interface.invariant
    # def ensureIdAndNameNotEqual(person):
    #     if person.id == person.name:
    #         raise interface.Invalid(
    #             "The id and name cannot be the same.")
    # 



class IStore( Interface ):
    """ represents a getpaid installation, should be a local site w/ getpaid local components installed
    """

class IPersistentOptions( Interface ):
    """
    a base interface that our persistent option annotation settings,
    can adapt to. specific schemas that want to have context stored
    annotation values should subclass from this interface, so they
    use adapation to get access to persistent settings. for example,
    settings = IMySettings(context)
    """


class IFormSchemas(Interface):
    """
    Utility for getting hold of the form schemas for a particular
    section. Any schema interface with fields that an implementor
    may want to chang should be given a section here rather than
    drectly using a hard-coded interface all over the place.
    """

    def getInterface(section):
        """
        Return the schema interface for the section specified.
        """

    def getPersistentBagClass(section):
        """
        Return the subclass of options.PersistentBag to use
        for storing field information for the specified section.
        """



#################################
# Payment Information Details
class IAbstractAddress( Interface ):
    """ base/common interface for all addresses"""

class IAddress( IAbstractAddress ):
    """ a physical address
    """
    first_line = schema.TextLine( title = _(u"Address 1"), description=_(u"Please Enter Your Address"))
    second_line = schema.TextLine( title = _(u"Address 2"), required=False )
    city = schema.TextLine( title = _(u"City") )
    country = schema.Choice( title = _(u"Country"),
                               vocabulary = "getpaid.countries")
    state = schema.Choice( title = _(u"State"),
                             vocabulary="getpaid.states")
    postal_code = schema.TextLine( title = _(u"Zip/Postal Code"))

class IShippingAddress( IAbstractAddress ):
    """ where to send goods
    """
    ship_same_billing = schema.Bool( title = _(u"Same as billing address"), required=False)
    ship_name = schema.TextLine( title = _(u"Full Name"), required=False)
    ship_organization = schema.TextLine( title = _(u"Organization/Company"), required=False)
    ship_first_line = schema.TextLine( title = _(u"Address 1"), required=False)
    ship_second_line = schema.TextLine( title = _(u"Address 2"), required=False)
    ship_city = schema.TextLine( title = _(u"City"), required=False)
    ship_country = schema.Choice( title = _(u"Country"),
                                    vocabulary = "getpaid.countries", required=False)
    ship_state = schema.Choice( title = _(u"State"),
                                  vocabulary="getpaid.states", required=False)
    ship_postal_code = schema.TextLine( title = _(u"Zip/Postal Code"), required=False)

class IBillingAddress( IAbstractAddress ):
    """ where to bill
    """
    bill_name = schema.TextLine( title = _(u"Full Name"))
    bill_organization = schema.TextLine( title = _(u"Organization/Company"), required=False)
    bill_first_line = schema.TextLine( title = _(u"Address 1"))
    bill_second_line = schema.TextLine( title = _(u"Address 2"), required=False )
    bill_city = schema.TextLine( title = _(u"City") )
    bill_country = schema.Choice( title = _(u"Country"),
                                    vocabulary = "getpaid.countries")
    bill_state = schema.Choice( title = _(u"State"),
                                  vocabulary="getpaid.states" )
    bill_postal_code = schema.TextLine( title = _(u"Zip/Postal Code"))

MarketingPreferenceVocabulary = SimpleVocabulary(
                                   map(SimpleVocabulary.createTerm,
                                       ( (True, "Yes", _(u"Yes")), (False, "No", _(u"No") ) )
                                       )
                                )

EmailFormatPreferenceVocabulary = SimpleVocabulary(
                                   map( lambda x: SimpleVocabulary.createTerm(*x),
                                       ( (True, "Yes", _(u"HTML")), (False, "No", _(u"Plain Text") ) )
                                       )
                                  )


class IUserContactInformation( Interface ):
    """docstring for IUserContactInformation"""

    name = schema.TextLine( title = _(u"Your Name"))

    phone_number = schema.TextLine( title = _(u"Phone Number"),
                                description = _(u"Only digits allowed - e.g. 3334445555 and not 333-444-5555 "))

    email = schema.TextLine(
                        title=_(u"Email"),
                        description = _(u"Contact Information"),
                        )

    marketing_preference = schema.Bool(
                                        title=_(u"Can we contact you with offers?"), 
                                        required=False,
                                        ) 

    email_html_format = schema.Choice( 
                                        title=_(u"Email Format"), 
                                        description=_(u"Would you prefer to receive rich html emails or only plain text"),
                                        vocabulary = EmailFormatPreferenceVocabulary,
                                        default = True,
                                        )


class IUserPaymentInformation( Interface ):
    """ A User's payment information to be optionally collected by the
    payment processor view.
    """

    name_on_card = schema.TextLine( title = _(u"Card Holder Name"),
                                description = _(u"Enter the full name, as it appears on the card. "))

    bill_phone_number = schema.TextLine( title = _(u"Phone Number"),
                                description = _(u"Only digits allowed - e.g. 3334445555 and not 333-444-5555 "))

    # DONT STORED PERSISTENTLY
    credit_card_type = schema.Choice( title = _(u"Credit Card Type"),
                                      source = "getpaid.core.accepted_credit_card_types",)

    credit_card = schema.TextLine( title = _(u"Credit Card Number"),
                                    description = _(u"Only digits allowed - e.g. 4444555566667777 and not 4444-5555-6666-7777 "))

    cc_expiration = schema.Date( title = _(u"Credit Card Expiration Date"),
                                    description = _(u"Select month and year"))

    cc_cvc = schema.TextLine(title = _(u"Credit Card Verfication Number", default=u"Credit Card Verification Number"),
                             description = _(u"For MC, Visa, and DC, this is a 3-digit number on back of the card.  For AmEx, this is a 4-digit code on front of card. "),
                             min_length = 3,
                             max_length = 4)
