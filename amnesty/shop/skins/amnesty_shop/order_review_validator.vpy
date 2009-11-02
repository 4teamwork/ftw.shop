## Script (Python) "order_review_validator"
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
if not r.get('order_confirmation', None):
  state.set(portal_status_message='Please confirm your order informations.')
return state
