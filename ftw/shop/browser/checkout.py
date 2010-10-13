from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.app.pagetemplate import viewpagetemplatefile

from z3c.form import field, button
from collective.z3cform.wizard import wizard
from plone.z3cform.layout import FormWrapper

from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import ICustomerInformation



class CustomerInfoStep(wizard.Step):
    prefix = 'step1'
    label = _(u"label_customer_info_step", default="Customer Information")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/customerinfo.pt')
    description = _(u'help_customer_info_step', default=u"")
    fields = field.Fields(ICustomerInformation)


class SummaryStep(wizard.Step):
    prefix = 'step2'
    label = _(u'label_summary_step', default="Order Summary")
    description = _(u'help_summary_step', default=u'')
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/summary.pt')


class CheckoutWizard(wizard.Wizard):
    steps = CustomerInfoStep, SummaryStep
    label = _(u"label_checkout_wizard", default="Checkout")
    index = viewpagetemplatefile.ViewPageTemplateFile('templates/checkout-wizard.pt')

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

        req = self.request

        session = self.session
        step1Form = session['step1']
        step2Form = session['step2']

        context = aq_inner(self.context)

        title = step1Form.get('title', 'N/A')

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

