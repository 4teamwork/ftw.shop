from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.registry.browser import controlpanel

from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _
from zope.app.form.browser import MultiSelectWidget

from plone.app.z3cform.layout import wrap_form, FormWrapper


class ShopConfigurationForm(controlpanel.RegistryEditForm):
    """Configuration form for the ftw.shop configlet
    """
    
    schema = IShopConfiguration
    form_fields = form.Fields(IShopConfiguration)
    label = _(u'label_shop_configuration', default=u"Shop configuration")
    template = ViewPageTemplateFile('templates/controlpanel.pt')
    #form_fields['payment_processor'].widget = MultiSelectWidget('fooo', ['foobar', 'barfoo'], None)
       
    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()
        
ShopConfigurationView = wrap_form(ShopConfigurationForm)