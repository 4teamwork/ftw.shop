from Acquisition import aq_inner
from zope.component import getMultiAdapter, adapts
from zope.component import getAdapters
from zope.component import getUtility
from zope.app.pagetemplate import viewpagetemplatefile
from zope.interface import implements, Interface

from plone.registry.interfaces import IRegistry

from z3c.form import field, button
from collective.z3cform.wizard import wizard
from plone.z3cform.layout import FormWrapper

from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import ICustomerInformation, IEmployeeNumber
from ftw.shop.interfaces import IContactInformationStep


class CustomerInfoStep(wizard.Step):
    implements(IContactInformationStep)
    adapts(Interface, Interface, Interface)
    prefix = 'step1'
    label = _(u"label_customer_info_step", default="Customer Information")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/customerinfo.pt')
    description = _(u'help_customer_info_step', default=u"")
    fields = field.Fields(ICustomerInformation)


class EmployeeNumberStep(wizard.Step):
    implements(IContactInformationStep)
    adapts(Interface, Interface, Interface)
    prefix = 'step1'
    label = _(u"label_employee_number_step", default="Employee Number")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/employee_number.pt')
    description = _(u'help_employee_number_step', default=u"")
    fields = field.Fields(IEmployeeNumber)


class SummaryStep(wizard.Step):
    prefix = 'step2'
    label = _(u'label_summary_step', default="Order Summary")
    description = _(u'help_summary_step', default=u'')
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/summary.pt')



class CheckoutWizard(wizard.Wizard):
    label = _(u"label_checkout_wizard", default="Checkout")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/checkout-wizard.pt')

    def __init__(self, context, request):
        super(CheckoutWizard, self).__init__(context, request)
        self.context = context
        self.request = request


    @property
    def steps(self):
        step1 = None
        contact_info_steps = getAdapters((self.context, self.request, self,), IContactInformationStep)
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IShopConfiguration)
        selected_contact_info_step = settings.contact_info_step
        
        for name, step_adapter in contact_info_steps:
            if name == selected_contact_info_step:
                step1 = step_adapter.__class__
        return (step1, SummaryStep)


    @button.buttonAndHandler(_(u'back_btn', default="back"),
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

    @button.buttonAndHandler(_(u'continue_btn', default='continue'),
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

    @button.buttonAndHandler(_(u'confirm_btn',default='confirm'),
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

        #req = self.request
        #session = self.session
        #step1Form = session['step1']
        #step2Form = session['step2']
        #context = aq_inner(self.context)
        #title = step1Form.get('title', 'N/A')

        self.request.SESSION['customer_data'] = {}
        self.request.SESSION['customer_data'].update(self.session['step1'])
        self.request.SESSION['order_confirmation'] = True

        self.request.SESSION[self.sessionKey] = {}
        self.sync()

        self.request.response.redirect('checkout')

class CheckoutView(FormWrapper):
    #layout = ViewPageTemplateFile("templates/layout.pt")
    #index = layout
    form = CheckoutWizard

    def __init__(self, context, request):
        cart_view = getMultiAdapter((context, request), name='cart_view')
        request['cart_view'] = cart_view
        FormWrapper.__init__(self, context, request)

