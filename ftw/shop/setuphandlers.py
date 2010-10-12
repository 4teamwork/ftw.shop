from Products.CMFCore.utils import getToolByName
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.browser.config import ShopConfiguration

# The profile id of your package:
PROFILE_ID = 'profile-ftw.shop:default'


def register_configuration_utility(context):
    sm = context.getSiteManager()

    if not sm.queryUtility(IShopConfiguration, name='shop_config'):
        sm.registerUtility(ShopConfiguration(),
                           IShopConfiguration,
                           'shop_config')


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ftw_shop-default.txt') is None:
        return
    site = context.getSite()
    register_configuration_utility(site)