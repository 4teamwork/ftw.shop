from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from amnesty.shop.config import CATEGORY_RELATIONSHIP
 
class CategoryView(BrowserView):
    """Default view for a catgory. Shows all contained shop items and categories.
    """
    
    __call__ = ViewPageTemplateFile('category.pt')

    def dummyitems(self):
        return []
        
        
#    @property
#    @instance.memoize
    def items(self):
        context = aq_inner(self.context)
        
        contents = context.getBRefs(CATEGORY_RELATIONSHIP)
        contents.sort(lambda x,y: cmp(x.getRankForCategory(context), y.getRankForCategory(context)))

        results = []
        for item in contents:
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
                    order_number = item.getSku_code(),
                    price = item.Price(),
                    addurl = '%s/addtocart' % item.absolute_url(),
                ))
            
            if item.portal_type == 'ShopMultiItem':
                # get variants
                variants = item.contentValues(filter={'portal_type':'ShopItemVariant'})
                variants_data = {}
                for variant in variants:
                    key = variant.getVariantLabel()
                    if not variants_data.has_key(key):
                        variants_data[key] = list()
                    variants_data[key].append(dict(
                        order_number = variant.getSku_code(),
                        title = variant.Title(),
                        price = variant.Price(),
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
    
