from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.z3cform.layout import wrap_form
from zope.formlib import form

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


class ShopConfigurationForm(RegistryEditForm):
    """Configuration form for the ftw.shop configlet
    """
    schema = IShopConfiguration
    form_fields = form.Fields(IShopConfiguration)
    label = _(u'label_shop_configuration', default=u"Shop configuration")

    def updateFields(self):
        super(ShopConfigurationForm, self).updateFields()

    def updateWidgets(self):
        super(ShopConfigurationForm, self).updateWidgets()

# BBB: For Plone3 compatibility, we need to override the template
# on the form wrapper, not the form itself, and use zope2's
# ViewPageTemplateFile, not zope3's
# See http://plone.org/products/dexterity/documentation/error/rendering-a-form-fails-with-attributeerror-str-object-has-no-attribute-other

ShopConfigurationView = wrap_form(ShopConfigurationForm, ControlPanelFormWrapper)
ShopConfigurationView.template = ViewPageTemplateFile('templates/controlpanel.pt')
