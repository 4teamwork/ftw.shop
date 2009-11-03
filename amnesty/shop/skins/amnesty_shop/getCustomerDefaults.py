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
customer = s.get('customer_data', {})
v = customer.get(field, None)
if v: return v

# last, look member preferences
pm = context.portal_membership
m = pm.getAuthenticatedMember()
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
