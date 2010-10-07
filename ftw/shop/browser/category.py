from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from Acquisition import aq_inner
from ftw.shop.config import CATEGORY_RELATIONSHIP
from Products.CMFCore.utils import getToolByName

class CategoryView(BrowserView):
    """Default view for a category. Shows all contained shop items and categories.
    """
    
    __call__ = ViewPageTemplateFile('category.pt')

    def dummyitems(self):
        return []
        
        
    @property
    @instance.memoize
    def items(self):
        """ get all shop items belonging to this category
        """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        
        
        results = []
        for item in self.category_contents:
            has_variations = item.Schema().getField('variation1_attribute').get(item) not in (None, '')
            # XXX
            image = None
            tag = None
            if image:
                tag = image.tag(scale='tile')
            if item.portal_type == 'ShopItem' and not has_variations:
                skuCode = item.Schema().getField('skuCode').get(item)
                results.append(dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    image = tag,
                    variants = None,
                    order_number = skuCode,
                    price = item.Schema().getField('price').get(item),
                    addurl = '%s/addtocart?skuCode=%s' % (item.absolute_url(), skuCode)
                ))
            
            if item.portal_type == 'ShopItem' and has_variations:
                # get variants
                #variants = item.contentValues(filter={'portal_type':'ShopItemVariant'})
                #variants = [v for v in variants if mtool.checkPermission('View', v)]
                variants = []
                variants_data = {}
                for variant in variants:
                    key = variant.variantLabel
                    if not variants_data.has_key(key):
                        variants_data[key] = list()
                    variants_data[key].append(dict(
                        order_number = variant.Schema().getField('skuCode').get(variant),
                        title = variant.Title(),
                        price = variant.Schema().getField('price').get(variant),
                        addurl = '%s/addtocart' % variant.absolute_url(), 
                    ))
                results.append(dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    image = tag,
                    variants = variants_data,
                ))
        return results

    #@property
    #@instance.memoize      
    def categories(self):
        """ get a list with all categories belonging to this category.
        """
        results = []
        for item in self.category_contents:
            image = None
            tag = None
            if image:
                tag = image.tag(scale='tile')
            if item.portal_type == 'ShopCategory':
                results.append(dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    image = tag,
                ))
        return results

    
    @property
    @instance.memoize        
    def category_contents(self):
        """ get all items (shop items, categories) belonging to this category.
        """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')   
        contents = context.getBRefs(CATEGORY_RELATIONSHIP)
        contents = [item for item in contents if mtool.checkPermission('View', item)]
        contents.sort(lambda x,y: cmp(x.getRankForCategory(context), y.getRankForCategory(context)))
        return contents
 