from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
     
class ShopItemView(BrowserView):
    """Default view for a shop item
    """
    #implements(IAIArticleView)
    
    __call__ = ViewPageTemplateFile('shopitem.pt')
    
    @property
    @instance.memoize    
    def item(self):
        context = aq_inner(self.context)
        if context.portal_type == 'ShopItem':
            return dict(
                order_number = context.skuCode,
                price = context.price,
                url = '%s/addtocart' % context.absolute_url(),
            )
        return None

    @property
    @instance.memoize
    def items(self):
        context = aq_inner(self.context)
        if context.portal_type == 'ShopMultiItem':
            ct = getToolByName(context, 'portal_catalog')
            query = {}
            query['path'] = {'query': '/'.join(context.getPhysicalPath()), 'depth': -1 }
            query['portal_type'] = 'ShopItemVariant'
            query['sort_on'] = 'getObjPositionInParent'

            results = {}
            mitems = ct(**query)
            for mitem in mitems:
                obj = mitem.getObject()
                key = obj.variantLabel
                if not results.has_key(key):
                    results[key] = list()
                results[key].append(dict(
                    order_number = obj.skuCode,
                    title = obj.Title(),
                    price = obj.price,
                    url = '%s/addtocart' % obj.absolute_url(),
                ))
            return results
  
            