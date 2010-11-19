from Acquisition import aq_inner, aq_parent
from ftw.shop.interfaces import IShopRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import ISiteRoot


def get_shop_root_object(context):
    """ Return the shop root object.
        If no shop root is defined, return the navigation root or the site
        root.
        Since this method traverses up the site until it finds an IShopRoot,
        it also works correctly on a site using LinguaPlone where there is
        one ShopRoot per language branch.
    """
    obj = aq_inner(context)
    while not IShopRoot.providedBy(obj) \
          and not INavigationRoot.providedBy(obj) \
          and not ISiteRoot.providedBy(obj):
        obj = aq_parent(obj)
    return obj
