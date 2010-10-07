## Script (Python) "update_categories"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=categories=[]
##title=
##
from Products.CMFCore.utils import getToolByName

catalog = getToolByName(context, 'portal_catalog')
old_uids = [obj.UID() for obj in context.listCategories()]

# add the checked categories
new_uids = [uid for uid in categories if uid not in old_uids]
for c in new_uids:
    context.addToCategory(c)

# remove the unchecked categories
uids_delete = [uid for uid in old_uids if uid not in categories]
categories_delete = uids_delete
for c in categories_delete:
    context.removeFromCategory(c)
  
#update ranks
for c in context.listCategories():
    rank = context.REQUEST.get('rank_%s' % c.UID(), 1)
    context.setRankForCategory(c, rank)

putils = getToolByName(context, 'plone_utils')
putils.addPortalMessage('Categories updated.', 'info')
return context.REQUEST.RESPONSE.redirect('%s' % (context.absolute_url()))
