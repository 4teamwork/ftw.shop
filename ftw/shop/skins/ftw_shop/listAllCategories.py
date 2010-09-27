## Script (Python) "listAllCategories"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=categoryUID=None
##title=
##
# return all Category instances except the context
# (that could be a Category instance too).
from Products.CMFCore.utils import getToolByName

portalPath = getToolByName(context, 'portal_url').getPortalPath()
ltool = getToolByName(context, 'portal_languages')
lang = ltool.getPreferredLanguage()

query = {}
query['portal_type'] = ['ShopCategory']
query['path'] = '%s/%s' % (portalPath, lang)
query['sort_on'] = 'sortable_title'

categories = context.portal_catalog.queryCatalog(query)
return [category.getObject() for category in categories if category.UID != categoryUID]