from Products.CMFCore.utils import getToolByName

# The profile id of your package:
PROFILE_ID = 'profile-ftw.shop:default'


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ftw_shop-default.txt') is None:
        return
    site = context.getSite()
    pass