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
            image = item.getImage()
            tag = None
            if image:
                tag = image.tag(scale='tile')
            if item.portal_type == 'ShopItem':
                results.append(dict(
                    title = item.Title(),
                    description = item.Description(),
                    url = item.absolute_url(),
                    image = tag,
                    variants = None,
                    order_number = item.skuCode,
                    price = item.price,
                    addurl = '%s/addtocart' % item.absolute_url(),
                ))
            
            if item.portal_type == 'ShopItem':
                # get variants
                variants = item.contentValues(filter={'portal_type':'ShopItemVariant'})
                variants = [v for v in variants if mtool.checkPermission('View', v)]
                variants_data = {}
                for variant in variants:
                    key = variant.variantLabel
                    if not variants_data.has_key(key):
                        variants_data[key] = list()
                    variants_data[key].append(dict(
                        order_number = variant.skuCode,
                        title = variant.Title(),
                        price = variant.price,
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
            image = item.getImage()
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
 