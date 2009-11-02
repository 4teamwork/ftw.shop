# Controller Python Script "order_review_redirect"
##bind context=context
##bind state=state
##parameters=
##title=
##

return state.set(next_action='traverse_to:string:checkout')
