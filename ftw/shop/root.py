from Acquisition import aq_inner, aq_parent
from ftw.shop.interfaces import IShopRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import ISiteRoot


def get_shop_root_object(context):
    """ return the shop root object.
        if no shop root is defined, return the navigation root or the site
        root.
    """
    obj = aq_inner(context)
    while not IShopRoot.providedBy(obj) \
          and not INavigationRoot.providedBy(obj) \
          and not ISiteRoot.providedBy(obj):
        obj = aq_parent(obj)
    return obj
