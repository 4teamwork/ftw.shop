from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.registry.browser import controlpanel

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _


class ShopConfigurationForm(controlpanel.RegistryEditForm):
    """Configuration form for the ftw.shop configlet
    """
    
    schema = IShopConfiguration
    form_fields = form.Fields(IShopConfiguration)
    label = _(u"Shop configuration")
    template = ViewPageTemplateFile('templates/controlpanel.pt')
       
    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()