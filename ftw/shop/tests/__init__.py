from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class FunctionalTestCase(TestCase):
    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal.portal_languages.manage_setLanguageSettings(
            supportedLanguages=['en'],
            defaultLanguage='en',
            setUseCombinedLanguageCodes=False,
        )

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
