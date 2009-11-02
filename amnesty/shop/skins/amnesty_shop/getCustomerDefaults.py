## Script (Python) "getCustomerDefaults"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field
##title=Return an apropriated value for a checkout form field
##


r = context.REQUEST
s = r.SESSION


# first, try to find a value in REQUEST
v = r.get(field, None)
if v: return v

# next, look in SESSION
if field in ['title',
             'firstname',
             'lastname',
             'newsletter',
             'email',
             'phone',
             'becomeAMember',
             'activeMember',
             'group',
             'comment'] and s.has_key('customer'):
    v = s['customer'].get(field, None)
    if v: return v
    
elif field in ['location_name',
               'street',
               'street_no',
               'street2',
               'zipcode',
               'city',] and s.has_key('customer_address'):
    v = s['customer_address'].get(field, None)
    if v: return v

# next, look at Member folder by CustomerInformation and
# AddressInformation objects

pm = context.portal_membership
m = pm.getAuthenticatedMember()
mf = pm.getHomeFolder()

# TODO: It's HARDCODED and need to be refactored to something more
# generic, following the interfaces register approach.

ci = getattr(mf, 'customer_information', None)
if ci:
    d = {'firstname' : 'getFirstname',
         'lastname'  : 'getLastname',
         'company'   : 'getCompany',
         'email'     : 'getEmail',
         'phoneNumbers':'getPhoneNumbers',
         'EUVATId':'getEUVATId',
         'comment':'getComment'
         }
         
    
    for k, v in d.items():
        if k == field:
            res=getattr(ci, v)()
            return res

    # ugly, but works!
    ai = ci.address_information_set.address_information
    if ai:
        d = {'location_name' : 'getLocation_name',
             'address1'      : 'getAddress1',
             'address2'      : 'getAddress2',
             'postal_code'   : 'getPostal_code',
             'city'          : 'getCity',
             'state'         : 'getState',
             'country'       : 'getCountry'}
        for k, v in d.items():
            if k == field:
                return getattr(ai, v)()

# last, look member preferences
if field in ['firstname', 'lastname', 'email']:
    if field == 'email':
        return m.getProperty('email', "")
    else:
        fullname = m.getProperty('fullname', "")
        # try to divide fullname into first and last name
        names = fullname.split(' ')
        if field == 'firstname':
            return names[0]
        elif field == 'lastname':
            try:
                return " ".join(names[1:])
            except IndexError:
                return ""

return ""
