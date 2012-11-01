from plone.app.upgrade.utils import loadMigrationProfile

def to_v11(context):
    loadMigrationProfile(context, 'profile-ftw.shop.upgrades:1.0-1.1')
