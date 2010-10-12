from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from OFS.SimpleItem import SimpleItem
from Products.Five.formlib import formbase

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _


class ShopConfigurationForm(formbase.EditFormBase):
    """Configuration form for the ftw.shop configlet
    """
    form_fields = form.Fields(IShopConfiguration)
    label = _(u"Shop configuration")


class ShopConfiguration(SimpleItem):
    """The configuration for ftw.shop
    """
    implements(IShopConfiguration)
    shop_name = FieldProperty(IShopConfiguration['shop_name'])


def form_adapter(context):
    return getUtility(IShopConfiguration, name='shop_config', context=context)
