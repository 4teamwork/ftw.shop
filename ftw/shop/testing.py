from ftw.testing import FunctionalSplinterTesting
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.testing import z2
from plone.testing import zca
from Testing.ZopeTestCase.utils import setupCoreSessions
from zope.configuration import xmlconfig


class ZCMLLayer(ComponentRegistryLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def setUp(self):
        super(ZCMLLayer, self).setUp()
        import ftw.shop.tests
        self.load_zcml_file('test.zcml', ftw.shop.tests)


ZCML_LAYER = ZCMLLayer()


class FtwShopLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(FtwShopLayer, self).setUpZope(app, configurationContext)

        # Include ZCML
        import z3c.autoinclude
        xmlconfig.file('meta.zcml', z3c.autoinclude,
                       context=configurationContext)
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            ' <includePlugins package="plone" />'
            ' <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        # Setup Session
        setupCoreSessions(app)

        z2.installProduct(app, 'ftw.shop')
        # import ftw.shop
        # xmlconfig.file('configure.zcml', ftw.shop)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.shop:default')


FTW_SHOP_FIXTURE = FtwShopLayer()
FTW_SHOP_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(FTW_SHOP_FIXTURE, ),
    name="ftw.shop:functional")
