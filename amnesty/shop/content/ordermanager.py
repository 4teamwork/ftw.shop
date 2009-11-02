
from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.Archetypes import atapi

from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema

from amnesty.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation
from amnesty.shop.config import PROJECTNAME
from zope.component import getMultiAdapter

schema = atapi.Schema((
    atapi.IntegerField('next_order_id',
        default="1",
        widget=atapi.IntegerWidget(
            label="Next Order ID",
            label_msgid='PloneMallOrder_label_next_order_id',
            description='Enter a value for Next Order ID.',
            description_msgid='PloneMallOrder_help_next_order_id',
            i18n_domain='plonemallorder',
        ),
        required=1,
    ),   
),
)


class OrderManager(UniqueObject, ATBTreeFolder):
    """
    Order Manager
    """
    security = ClassSecurityInfo()
    meta_type = 'OrderManager' 
    schema = ATBTreeFolderSchema + schema

    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        ATBTreeFolder.__init__(self,'portal_ordermanager')


    security.declareProtected("Buy item", 'addOrder')
    def addOrder(self):
        '''
        Add a new Order and returns the order id.
        '''
 
        session = self.REQUEST.SESSION
        
        # check for customer data
        customer_data = session.get('customer_data', {})
        if not customer_data:
            raise MissingCustomerInformation
        
        # check for order confirmation
        if not self.REQUEST.get('order_confirmation', None):
            raise MissingOrderConfirmation            

        # calculate the next order id
        order_id = self.getNextOrderId()
        
        # change security context to owner
        user = self.getWrappedOwner()
        newSecurityManager(self.REQUEST, user)
        
        # create Order
        self.invokeFactory('ShopOrder', id=order_id)
        order = getattr(self, str(order_id))

        # calc order number
        now  = DateTime()
        order_number = '%03d%s%04d' % (now.dayOfYear()+500, now.yy(), order_id )

        order.setTitle(order_number)



        session = self.REQUEST.SESSION

        # process the customer information from SESSION
        customer_data = session.get('customer', {})
        order.setCustomerData(customer_data)

        # store cart in order
        cart_view = getMultiAdapter((self, self.REQUEST), name=u'cart_view')
        cart_data = cart_view.cart_items()
        order.setCartData(cart_data)


        # Payment Method (pm)
        #pm = AIOnAccountPayment()
        #pm.processPayment(o)

        noSecurityManager()
        
        return order_number

    security.declareProtected("Manage", 'sendOrderMail')
    def sendOrderMail(self, orderid):
        """
        Send order confirmation mail of the order with the specified orderid.
        Can be used if initial sendig of order mail failed for some reason.
        """
        o = getattr(self, str(orderid))
        #pm = AIOnAccountPayment()
        #pm.processPayment(o)
        return "sent mail for order %s." % orderid
    
        

    security.declareProtected("View", 'getOrderById')
    def getOrderById(self, order_id):
        '''
        Return an Order but its order id.
        '''

        return self._getOb(str(order_id), None)
    

    def getNextOrderId(self):
        currid=self.getNext_order_id()
        nextid=int(currid) + 1
        self.setNext_order_id(nextid)
        return currid


atapi.registerType(OrderManager, PROJECTNAME)