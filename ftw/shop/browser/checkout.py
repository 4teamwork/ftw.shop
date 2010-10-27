import base64
import simplejson
from datetime import datetime, timedelta

from zope.component import getMultiAdapter, adapts
from zope.component import getAdapters
from zope.component import getUtility
from zope.app.pagetemplate import viewpagetemplatefile
from zope.interface import implements, Interface

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry

from z3c.form import field, button
from collective.z3cform.wizard import wizard
from plone.z3cform.layout import FormWrapper

from ftw.shop.config import SESSION_ADDRESS_KEY, SESSION_ORDERS_KEY, COOKIE_ADDRESS_KEY
from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IDefaultContactInformation
from ftw.shop.interfaces import IContactInformationStep
from ftw.shop.interfaces import IContactInformationStepGroup
from ftw.shop.interfaces import IPaymentProcessor
from ftw.shop.interfaces import IPaymentProcessorChoiceStep
#from ftw.shop.interfaces import IPaymentProcessorDetailsStep
from ftw.shop.interfaces import IPaymentProcessorStepGroup

from ftw.shop.interfaces import IDefaultPaymentProcessorChoice


class DefaultContactInfoStep(wizard.Step):
    implements(IContactInformationStep)
    prefix = 'contact_information'
    label = _(u"label_default_contact_info_step", default="Contact Information")
    description = _(u'help_default_contact_info_step', default=u"")
    fields = field.Fields(IDefaultContactInformation)

    def __init__(self, context, request, wiz):
        super(wizard.Step, self).__init__(context, request)
        self.wizard = wiz
        PREFILL_FIELDS = ['title', 'firstname', 'lastname', 'email', 'street1',
                          'street2', 'phone', 'zipcode', 'city', 'country', 
                          'newsletter']
        
        if COOKIE_ADDRESS_KEY in request:
            # Prefill contact data with values from cookie
            cookie_data = simplejson.loads(base64.b64decode(request[COOKIE_ADDRESS_KEY]))
            for key in cookie_data.keys():
                if isinstance(cookie_data[key], basestring):
                    cookie_data[key] = unicode(cookie_data[key])
                    
            for fieldname in PREFILL_FIELDS:
                self.fields[fieldname].field.default = cookie_data[fieldname]
            
        elif SESSION_ADDRESS_KEY in request.SESSION.keys():
            # Prefill contact data form with values from session
            contact_info = request.SESSION[SESSION_ADDRESS_KEY]
            for fieldname in PREFILL_FIELDS:
                self.fields[fieldname].field.default = contact_info[fieldname]

    def updateWidgets(self):
        super(DefaultContactInfoStep, self).updateWidgets()
        self.widgets['zipcode'].size = 5



class DefaultContactInfoStepGroup(object):
    implements(IContactInformationStepGroup)
    adapts(Interface, Interface, Interface)
    steps = (DefaultContactInfoStep,)
    
    def __init__(self, context, request, foo):
        pass

class DefaultPaymentProcessorChoiceStep(wizard.Step):
    implements(IPaymentProcessorChoiceStep)
    prefix = 'payment_processor_choice'
    label = _(u"label_default_payment_processor_choice_step", default="Payment Processor")
    description = _(u'help_default_payment_processor_choice_step', default=u"")
    fields = field.Fields(IDefaultPaymentProcessorChoice)
    

#class DefaultPaymentProcessorDetailsStep(wizard.Step):
#    implements(IPaymentProcessorDetailsStep)
#    prefix = 'step2'
#    label = _(u"label_default_payment_processor_details_step", default="Payment Processor Details")
#    description = _(u'help_default_payment_processor_details_step', default=u"")
#    fields = field.Fields(IDefaultPaymentProcessorDetails)


class DefaultPaymentProcessorStepGroup(object):
    implements(IPaymentProcessorStepGroup)
    adapts(Interface, Interface, Interface)
    steps = (DefaultPaymentProcessorChoiceStep,)
    
    def __init__(self, context, request, foo):
        pass
    
class InvoicePaymentProcessor(object):
    implements(IPaymentProcessor)
    adapts(Interface, Interface, Interface)
    
    external = False
    url = None
    title = "Gegen Rechnung"
    
    def __init__(self, context, request, foo):
        pass


class OrderReviewStep(wizard.Step):
    prefix = 'step3'
    label = _(u'label_order_review_step', default="Order Review")
    description = _(u'help_order_review_step', default=u'')
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/checkout/order_review.pt')



class CheckoutWizard(wizard.Wizard):
    label = _(u"label_checkout_wizard", default="Checkout")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/checkout-wizard.pt')

    def __init__(self, context, request):
        super(CheckoutWizard, self).__init__(context, request)
        self.context = context
        self.request = request

        
    def getSelectedPaymentProcessor(self):
        payment_processor = None
        try:
            payment_processor_name = self.session['payment_processor_choice']['payment_processor']
        except KeyError:
            payment_processor_name = self.request.SESSION['payment_processor_choice']['payment_processor']
        for name, adapter in getAdapters((self.context, None, self.context,), IPaymentProcessor):
            if name == payment_processor_name:
                payment_processor = adapter
        return payment_processor
        
    @property
    def steps(self):
        contact_info_steps = ()
        contact_info_step_groups = getAdapters((self.context, self.request, self,), IContactInformationStepGroup)
        payment_processor_step_groups = getAdapters((self.context, self.request, self,), IPaymentProcessorStepGroup)
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopConfiguration)
        selected_contact_info_step_group = settings.contact_info_step_group
        
        for name, step_group_adapter in contact_info_step_groups:
            if name == selected_contact_info_step_group:
                contact_info_steps = step_group_adapter.steps
                
        selected_payment_processor_step_group = "ftw.shop.DefaultPaymentProcessorStepGroup"        
        for name, step_group_adapter in payment_processor_step_groups:
            if name == selected_payment_processor_step_group:
                payment_processor_steps = step_group_adapter.steps
                

        return contact_info_steps + payment_processor_steps + (OrderReviewStep, )


    @button.buttonAndHandler(_(u'btn_back', default="Back"),
                             name='back',
                             condition=lambda form:not form.onFirstStep)

    def handleBack(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            errorMessage ='<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage

        else:
            self.currentStep.applyChanges(data)
            self.updateCurrentStep(self.currentIndex - 1)

            # Back can change the conditions for the finish button,
            # so we need to reconstruct the button actions, since we
            # do not redirect.
            self.updateActions()

    @button.buttonAndHandler(_(u'btn_continue', default='Next'),
                             name='continue',
                             condition=lambda form:not form.onLastStep)
    def handleContinue(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            errorMessage ='<ul>'
            for error in errors:
                if errorMessage.find(error.message):
                    errorMessage += '<li>' + error.message + '</li>'
            errorMessage += '</ul>'
            self.status = errorMessage
        else:

            self.currentStep.applyChanges(data)
            self.updateCurrentStep(self.currentIndex + 1)

            # Proceed can change the conditions for the finish button,
            # so we need to reconstruct the button actions, since we
            # do not redirect.
            self.updateActions()

    @button.buttonAndHandler(_(u'btn_finish',default='Finish'),
                             name='finish',
                             condition=lambda form:form.allStepsFinished or form.onLastStep)
    def handleFinish(self, action):
        data, errors = self.currentStep.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        else:
            self.status = self.successMessage
            self.finished = True
        self.currentStep.applyChanges(data)
        self.finish()
        
        self.request.SESSION[SESSION_ADDRESS_KEY] = {}
        self.request.SESSION[SESSION_ADDRESS_KEY].update(self.session['contact_information'])
        self.request.SESSION['order_confirmation'] = True
        self.request.SESSION['payment_processor_choice'] = {}
        self.request.SESSION['payment_processor_choice'].update(self.session['payment_processor_choice'])

        # Save contact information in a cookie to prefill form if customer returns
        cookie_value = base64.b64encode(simplejson.dumps(self.session['contact_information']))
        expiry_date = (datetime.now() + timedelta(days=90)).strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        self.request.RESPONSE.setCookie(COOKIE_ADDRESS_KEY, 
                                        cookie_value, 
                                        expires=expiry_date)

        self.request.SESSION[self.sessionKey] = {}
        self.sync()
        
        pp = self.getSelectedPaymentProcessor()
        if pp.external:
            self.request.SESSION['external-processor-url'] = pp.url
            self.request.SESSION['external-processor-url'] = "http://localhost:8077/"

        self.request.response.redirect('checkout')

class CheckoutView(FormWrapper):
    #layout = ViewPageTemplateFile("templates/layout.pt")
    #index = layout
    form = CheckoutWizard

    def __init__(self, context, request):
        cart_view = getMultiAdapter((context, request), name='cart_view')
        request['cart_view'] = cart_view
        FormWrapper.__init__(self, context, request)

class ExternalPaymentProcessorView(BrowserView):
    """Redirects to an external payment processor
    """
    __call__ = ViewPageTemplateFile('templates/checkout/external.pt')
