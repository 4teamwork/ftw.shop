from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from OFS.SimpleItem import SimpleItem
from Products.Five.formlib import formbase

from plone.app.registry.browser import controlpanel

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _


class ShopConfigurationForm(controlpanel.RegistryEditForm):
    """Configuration form for the ftw.shop configlet
    """
    
    schema = IShopConfiguration
    form_fields = form.Fields(IShopConfiguration)
    label = _(u"Shop configuration")
       
    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()


class ShopConfigurationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ShopConfigurationForm
