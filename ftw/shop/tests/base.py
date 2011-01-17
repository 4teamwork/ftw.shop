"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
from decimal import Decimal

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
import zope.event
from zope.component import getMultiAdapter
from zope.interface import Interface
from Products.Archetypes.event import ObjectInitializedEvent
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from ftw.shop.interfaces import IVariationConfig

# Mock data to be used in various tests in ftw.shop but also
# other ftwshop.* products

MOCK_CUSTOMER = {'title': u'Mr.',
                 'firstname': u'Hugo',
                 'lastname': u'Boss',
                 'company': u'ACME Corp.',
                 'street1': u'Teststreet 23',
                 'street2': u'',
                 'zipcode': u'56789',
                 'city': u'Exampletown',
                 'email': u'hugo@example.org',
                 'phone': u'099 999 99 99',
                 'country': u'Switzerland',
                 'newsletter': False}

MOCK_SHIPPING = {'title': u'Mr.',
                'firstname': u'Hugo',
                'lastname': u'Boss',
                'company': u'ACME Corp.',
                'street1': u'Shippingstreet 42',
                'street2': u'',
                'zipcode': u'4242',
                'city': u'Exampletown'}

MOCK_CART = {'12345': {'quantity':2,
                       'price': '4.15',
                       'title': 'Item Title',
                       'total': '8.30',
                       'supplier_name': 'Supplier Name',
                       'supplier_email': 'supplier@example.org'}}


# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.
    
    fiveconfigure.debug_mode = True
    import ftw.shop
    
    zcml.load_config('configure.zcml', ftw.shop)
    
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage()
    # instead of installProduct().
    # This is *only* necessary for packages outside the Products.*
    # namespace which are also declared as Zope 2 products, using
    # <five:registerPackage /> in ZCML.

    # We may also need to load dependencies, e.g.:
    #   ztc.installPackage('borg.localrole')

    ztc.installPackage('ftw.shop')    
    

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['ftw.shop'])

class FtwShopTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

    def afterSetUp(self):
        # Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        self.setRoles(('Manager',))

        # Use helper method to set up shop root at portal.shop
        init_shop = getMultiAdapter((self.portal, self.portal.REQUEST),
                                    Interface, 'initialize-shop-structure')
        init_shop()

        # Create a shop category
        self.portal.shop.invokeFactory("ShopCategory", "products")

        # Create a Shop Item with no variations
        self.portal.shop.products.invokeFactory('ShopItem', 'movie')
        self.movie = self.portal.shop.products['movie']
        self.movie.getField('skuCode').set(self.movie, "12345")
        self.movie.getField('price').set(self.movie, "7.15")
        self.movie.getField('title').set(self.movie, "A Movie")
        self.movie.getField('description').set(self.movie, "A Shop Item with no variations")

        # Fire ObjectInitializedEvent to add item to containing category
        event = ObjectInitializedEvent(self.movie, self.portal.REQUEST)
        zope.event.notify(event)

        self.movie_vc = IVariationConfig(self.movie)

        # Create a Shop Item with one variation
        self.portal.shop.products.invokeFactory('ShopItem', 'book')
        self.book = self.portal.shop.products['book']
        self.book.getField('title').set(self.book, 'Professional Plone Development')
        self.book.getField('description').set(self.book, 'A Shop Item with one variation')
        self.book.getField('variation1_attribute').set(self.book, 'Cover')
        self.book.getField('variation1_values').set(self.book, ['Hardcover', 'Paperback'])

        # Fire ObjectInitializedEvent to add item to containing category
        event = ObjectInitializedEvent(self.book, self.portal.REQUEST)
        zope.event.notify(event)

        self.book_vc = IVariationConfig(self.book)
        book_var_dict = {
        'hardcover': {'active': True, 
                      'price': Decimal('1.00'),
                      'skuCode': 'b11',
                      'description': 'A hard and durable cover',
                      'hasUniqueSKU': True},
        'paperback': {'active': True, 
                      'price': Decimal('2.00'),
                      'skuCode': 'b22',
                      'description': 'A less durable but cheaper cover',
                      'hasUniqueSKU': True},
        }
        self.book_vc.updateVariationConfig(book_var_dict)

        # Create a Shop Item with two variations
        self.portal.shop.products.invokeFactory('ShopItem', 't-shirt')
        self.tshirt = self.portal.shop.products['t-shirt']
        self.tshirt.getField('title').set(self.tshirt, 'A T-Shirt')
        self.tshirt.getField('description').set(self.tshirt, 'A Shop Item with two variations')
        self.tshirt.getField('variation1_attribute').set(self.tshirt, 'Color')
        self.tshirt.getField('variation1_values').set(self.tshirt, ['Red', 'Green', 'Blue'])
        self.tshirt.getField('variation2_attribute').set(self.tshirt, 'Size')
        self.tshirt.getField('variation2_values').set(self.tshirt, ['S', 'M', 'L'])

        # Fire ObjectInitializedEvent to add item to containing category
        event = ObjectInitializedEvent(self.tshirt, self.portal.REQUEST)
        zope.event.notify(event)

        self.tshirt_vc = IVariationConfig(self.tshirt)
        tshirt_var_dict = {
        'red-s': {'active': True, 'price': Decimal('1.00'), 'skuCode': '11', 'description': '', 'hasUniqueSKU': True},
        'red-m': {'active': True, 'price': Decimal('2.00'), 'skuCode': '22', 'description': '', 'hasUniqueSKU': True},
        'red-l': {'active': True, 'price': Decimal('3.00'), 'skuCode': '33', 'description': '', 'hasUniqueSKU': True},
        'green-s': {'active': True, 'price': Decimal('4.00'), 'skuCode': '44', 'description': '', 'hasUniqueSKU': True},
        'green-m': {'active': True, 'price': Decimal('5.00'), 'skuCode': '55', 'description': '', 'hasUniqueSKU': True},
        'green-l': {'active': True, 'price': Decimal('6.00'), 'skuCode': '66', 'description': '', 'hasUniqueSKU': True},
        'blue-s': {'active': True, 'price': Decimal('7.00'), 'skuCode': '77', 'description': '', 'hasUniqueSKU': True},
        'blue-m': {'active': True, 'price': Decimal('8.00'), 'skuCode': '88', 'description': '', 'hasUniqueSKU': True},
        'blue-l': {'active': True, 'price': Decimal('9.00'), 'skuCode': '99', 'description': '', 'hasUniqueSKU': True},
        }
        self.tshirt_vc.updateVariationConfig(tshirt_var_dict)

        # Create a subcategory below the shop root
        self.portal.shop.products.invokeFactory("ShopCategory", "subcategory")
        self.subcategory = self.portal.shop.products.subcategory

        # Fire ObjectInitializedEvent to add category to containing category
        event = ObjectInitializedEvent(self.subcategory, self.portal.REQUEST)
        zope.event.notify(event)

        self.setRoles(('Member',))


    class Session(dict):
        def set(self, key, value):
            self[key] = value

        def invalidate(self):
            self.clear()


    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()


class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
