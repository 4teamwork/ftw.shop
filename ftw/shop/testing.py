from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Testing.ZopeTestCase.utils import setupCoreSessions
from zope.configuration import xmlconfig
import ftw.shop.tests.builders


class FtwShopLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)
        setupCoreSessions(app)
        z2.installProduct(app, 'ftw.shop')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.shop:default')


FTW_SHOP_FIXTURE = FtwShopLayer()
FTW_SHOP_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SHOP_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.shop:functional")

FTW_SHOP_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_SHOP_FIXTURE, ), name="ftw.shop:integration")
