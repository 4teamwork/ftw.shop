from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    # plone.app.registry 1.0b1
    from plone.app.registry.browser.form import RegistryEditForm
    from plone.app.registry.browser.form import ControlPanelFormWrapper
except ImportError:
    # plone.app.registry 1.0b2+
    from plone.app.registry.browser.controlpanel import RegistryEditForm
    from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper


from ftw.shop.interfaces import IShopConfiguration
from ftw.shop import shopMessageFactory as _
from zope.app.form.browser import MultiSelectWidget

from plone.app.z3cform.layout import wrap_form, FormWrapper


class ShopConfigurationForm(RegistryEditForm):
    """Configuration form for the ftw.shop configlet
    """
    
    schema = IShopConfiguration
    form_fields = form.Fields(IShopConfiguration)
    label = _(u'label_shop_configuration', default=u"Shop configuration")
    #template = ViewPageTemplateFile('templates/controlpanel.pt')
       
    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()

ShopConfigurationView = wrap_form(ShopConfigurationForm, ControlPanelFormWrapper)
ShopConfigurationView.template = ViewPageTemplateFile('templates/controlpanel.pt')
