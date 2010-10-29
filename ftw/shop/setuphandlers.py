from z3c.saconfig import named_scoped_session
from z3c.saconfig.interfaces import IScopedSession
from zope.component import queryUtility

from ftw.shop.utils import create_session
from ftw.shop.model.order import Order

# The profile id of our package:
PROFILE_ID = 'profile-ftw.shop:default'

MODELS = [Order]


def create_sql_tables():
    """Creates the sql tables for the models.
    """

    session = create_session()
    for model in MODELS:
        getattr(model, 'metadata').create_all(session.bind)


def FtwShopSessionName(object):
    return named_scoped_session('ftw.shop')


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ftw_shop-default.txt') is None:
        return

    if queryUtility(IScopedSession, 'ftw.shop'):
        create_sql_tables()
