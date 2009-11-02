# Controller Python Script "customer_redirect"
##bind context=context
##bind state=state
##parameters=
##title=
##
# store request data in session
r = context.REQUEST
s = r.SESSION

s['customer_data'] = {
    'title' : r.get('title'),
    'firstname' : r.get('firstname'),
    'lastname' : r.get('lastname'),
    'email' : r.get('email'),
    'newsletter' : r.get('newsletter'),
    'phone' : r.get('phone'),
    'comments':r.get('comments'),
    'street' : r.get('street'),
    'street2' : r.get('street2'),
    'zipcode' : r.get('zipcode'),
    'city' : r.get('city'),
    'country' : r.get('country'),
}

return state.set(next_action='traverse_to:string:checkout')
