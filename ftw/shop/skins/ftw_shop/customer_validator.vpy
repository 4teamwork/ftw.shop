## Script (Python) "customer_information_validator"
##bind container=container
##bind context=context
##bind state=state
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
r = context.REQUEST
d = {'title' : 'Title',
     'firstname' : 'First Name',
     'lastname' : 'Last Name',
     'email' : 'Email',
     'street' : 'Street',
     'zipcode' : 'ZIP Code',
     'city' : 'City',
     }
for k, v in d.items():
  f = r.get(k, None)
  if not f:
    state.setError(k, 'Please enter a value',
                       msgid="error_required", new_status='failure')
    
if r.get('activeMember', None):
    if not r.get('group', None):
        state.setError('group', 'Please specify your AI group.',
                       msgid="error_required", new_status='failure')
        

if state.getErrors():
    state.set(portal_status_message='Please correct the indicated errors.')    

return state
