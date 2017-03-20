import transaction
from decimal import Decimal
from Products.CMFCore.utils import getToolByName
import simplejson

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.i18n import translate

from ftw.shop import shopMessageFactory as _
from ftw.shop.interfaces import IVariationConfig


class ShopItemView(BrowserView):
    """Default view for a shop item
    """

    __call__ = ViewPageTemplateFile('templates/shopitem.pt')

    single_item_template = ViewPageTemplateFile('templates/listing/single_item.pt')
    one_variation_template = ViewPageTemplateFile('templates/listing/one_variation_compact.pt')
    two_variations_template = ViewPageTemplateFile('templates/listing/two_variations_compact.pt')

    @property
    def depth(self):
        return len(self.getVariationAttributes())

    def getItems(self):
        """Returns a list with this item as its only element,
        so the listing viewlet can treat it like a list of items
        """
        context = aq_inner(self.context)
        return [context]

    def single_item(self, item):
        return self.single_item_template(item=item)

    def one_variation(self, item):
        return self.one_variation_template(item=item)

    def two_variations(self, item):
        return self.two_variations_template(item=item)

    def getItemDatas(self):
        """Returns a dictionary of an item's properties to be used in
        templates. If the item has variations, the variation config is
        also included.
        """
        results = []
        for item in self.getItems():
            varConf = IVariationConfig(item)
            has_variations = varConf.hasVariations()

            image = item.getField('image')
            if image and image.get_size(item):
                hasImage = True
                tag = image.tag(item, scale='tile')
            else:
                hasImage = False
                tag = None

            if has_variations:
                skuCode = None
                price = None
            else:
                varConf = None
                skuCode = item.Schema().getField('skuCode').get(item)
                price = item.Schema().getField('price').get(item)

            results.append(dict(item = item,
                                title = item.Title(),
                                description = item.Description(),
                                url = item.absolute_url(),
                                hasImage = hasImage,
                                imageTag = tag,
                                variants = None,
                                skuCode = skuCode,
                                price = price,
                                showPrice = item.getField('showPrice').get(item),
                                unit=item.getField('unit').get(item),
                                uid = item.UID(),
                                varConf = varConf,
                                hasVariations = has_variations,
                                selectable_dimensions = item.getSelectableDimensions()))
        return results

    def getVariationsConfig(self):
        """Returns the variation config for the item currently being viewed
        """
        context = aq_inner(self.context)
        variation_config = IVariationConfig(context)
        return variation_config

    def getVarDictsJSON(self):
        """Returns a JSON serialized dict with UID:varDict pairs, where UID
        is the ShopItem's UID and varDict is the item's variation dict.
        This is being used for the compact category view where inactive
        item variations must not be buyable.
        """
        varDicts = {}
        items = self.getItemDatas()
        for item in items:
            uid = item['uid']
            varConf = item['varConf']
            if varConf is not None:
                varDicts[uid] = dict(varConf.getVariationDict())
            else:
                varDicts[uid] = {}

            # Convert Decimals to Strings for serialization
            varDict = varDicts[uid]
            for vcode in varDict.keys():
                i = varDict[vcode]
                for k in i.keys():
                    val = i[k]
                    if isinstance(val, Decimal):
                        val = str(val)
                        i[k] = val

        return simplejson.dumps(varDicts)


class EditVariationsView(BrowserView):
    """View for editing ShopItem Variations
    """
    template = ViewPageTemplateFile('templates/edit_variations.pt')

    def __call__(self):
        """
        Self-submitting form that displays ShopItem Variations
        and updates them

        """
        form = self.request.form

        if form.get('remove_level'):
            variation_config = IVariationConfig(self.context)
            variation_config.remove_level()

        if form.get('reduce_level'):
            variation_config = IVariationConfig(self.context)
            variation_config.reduce_level()

        if form.get('add_level'):
            variation_config = IVariationConfig(self.context)
            variation_config.add_level()


        if form.get('addvalue'):
            fn = None
            idx_and_pos = form.get('addvalue')
            idx, pos = idx_and_pos.split('-')
            idx = int(idx)
            pos = int(pos) + 1

            if idx == 0:
                fn = 'variation1_values'
            elif idx == 1:
                fn = 'variation2_values'

            variation_config = IVariationConfig(self.context)
            values = list(self.context.getField(fn).get(self.context))
            var_dict = variation_config.getVariationDict()
            new_var_dict = {}
            pps = getMultiAdapter((self.context, self.request), name='plone_portal_state')
            language = pps.language()
            new_description = translate(_('label_new_description', default=u'New description'), domain='ftw.shop', context=self.context, target_language=language)
            DEFAULT_VARDATA = {'active':True, 'price': '0.00', 'skuCode': '99999', 'description': new_description}


            if len(variation_config.getVariationAttributes()) == 2:
                values1 = list(self.context.getField('variation1_values').get(self.context))
                values2 = list(self.context.getField('variation2_values').get(self.context))

                # Create a dict mapping old combination indexes to the new ones
                code_map = {}
                if idx == 0:
                    for i in range(len(values1)):
                        for j in range(len(values2)):
                            old_vcode = "var-%s-%s" % (i, j)
                            if i >= pos:
                                new_vcode = "var-%s-%s" % (i + 1, j)
                                code_map[old_vcode] = new_vcode
                            else:
                                code_map[old_vcode] = old_vcode
                elif idx == 1:
                    for i in range(len(values1)):
                        for j in range(len(values2)):
                            old_vcode = "var-%s-%s" % (i, j)
                            if j >= pos:
                                new_vcode = "var-%s-%s" % (i, j + 1)
                                code_map[old_vcode] = new_vcode
                            else:
                                code_map[old_vcode] = old_vcode

                # Based on the code map, reorder the var_dict
                for old_vcode in code_map.keys():
                    new_vcode = code_map[old_vcode]
                    new_var_dict[new_vcode] = var_dict[old_vcode]

                # Now add some default variation data for the value just added
                if idx == 0:
                    for j in range(len(values2)):
                        vcode = "var-%s-%s" % (pos, j)
                        new_var_dict[vcode] = DEFAULT_VARDATA
                elif idx == 1:
                    for i in range(len(values1)):
                        vcode = "var-%s-%s" % (i, pos)
                        new_var_dict[vcode] = DEFAULT_VARDATA


            elif len(variation_config.getVariationAttributes()) == 1:
                assert(idx == 0)
                values1 = list(self.context.getField('variation1_values').get(self.context))

                # Create a dict mapping old combination indexes to the new ones
                code_map = {}
                for i in range(len(values1)):
                    old_vcode = "var-%s" % (i)
                    if i >= pos:
                        new_vcode = "var-%s" % (i + 1)
                        code_map[old_vcode] = new_vcode
                    else:
                        code_map[old_vcode] = old_vcode

                # Based on the code map, reorder the var_dict
                for old_vcode in code_map.keys():
                    new_vcode = code_map[old_vcode]
                    new_var_dict[new_vcode] = var_dict[old_vcode]

                # Now add some default variation data for the value just added
                vcode = "var-%s" % pos
                new_var_dict[vcode] = DEFAULT_VARDATA


            # Finally purge and update the var_dict
            variation_config.purge_dict()
            variation_config.updateVariationConfig(new_var_dict)
            pps = getMultiAdapter((self.context, self.request), name='plone_portal_state')
            language = pps.language()
            new_value = translate(_('label_new_value', default=u'New value'), domain='ftw.shop', context=self.context, target_language=language)
            values.insert(pos, new_value)
            self.context.getField(fn).set(self.context, values)



        if form.get('delvalue'):
            fn = None
            idx_and_pos = form.get('delvalue')
            idx, pos = idx_and_pos.split('-')
            idx = int(idx)
            pos = int(pos)

            if idx == 0:
                fn = 'variation1_values'
            elif idx == 1:
                fn = 'variation2_values'
            values = list(self.context.getField(fn).get(self.context))


            variation_config = IVariationConfig(self.context)
            var_dict = variation_config.getVariationDict()
            new_var_dict = {}

            if len(variation_config.getVariationAttributes()) == 2:
                values1 = list(self.context.getField('variation1_values').get(self.context))
                values2 = list(self.context.getField('variation2_values').get(self.context))

                # Create a dict mapping old combination indexes to the new ones
                code_map = {}
                if idx == 0:
                    for i in range(len(values1)):
                        for j in range(len(values2)):
                            old_vcode = "var-%s-%s" % (i, j)
                            if i > pos:
                                new_vcode = "var-%s-%s" % (i - 1, j)
                                code_map[old_vcode] = new_vcode
                            elif i == pos:
                                code_map[old_vcode] = None
                            else:
                                code_map[old_vcode] = old_vcode
                elif idx == 1:
                    for i in range(len(values1)):
                        for j in range(len(values2)):
                            old_vcode = "var-%s-%s" % (i, j)
                            if j > pos:
                                new_vcode = "var-%s-%s" % (i, j - 1)
                                code_map[old_vcode] = new_vcode
                            elif j == pos:
                                code_map[old_vcode] = None
                            else:
                                code_map[old_vcode] = old_vcode

                # Based on the code map, reorder the var_dict
                for old_vcode in code_map.keys():
                    new_vcode = code_map[old_vcode]
                    new_var_dict[new_vcode] = var_dict[old_vcode]


            elif len(variation_config.getVariationAttributes()) == 1:
                assert(idx == 0)
                values1 = list(self.context.getField('variation1_values').get(self.context))

                # Create a dict mapping old combination indexes to the new ones
                code_map = {}
                for i in range(len(values1)):
                    old_vcode = "var-%s" % (i)
                    if i >= pos:
                        new_vcode = "var-%s" % (i - 1)
                        code_map[old_vcode] = new_vcode
                    else:
                        code_map[old_vcode] = old_vcode

                # Based on the code map, reorder the var_dict
                for old_vcode in code_map.keys():
                    new_vcode = code_map[old_vcode]
                    new_var_dict[new_vcode] = var_dict[old_vcode]


            # # Finally purge and update the var_dict
            variation_config.purge_dict()
            variation_config.updateVariationConfig(new_var_dict)

            values.pop(int(pos))
            self.context.getField(fn).set(self.context, values)




        if form.get('update_structure'):
            var_config = IVariationConfig(self.context)
            vattr0 = form.get('vattr-0', None)
            vattr1 = form.get('vattr-1', None)

            if len(var_config.getVariationAttributes()) >= 1:
                self.context.getField('variation1_attribute').set(self.context, vattr0)
                new_values = []
                for i in range(len(var_config.getVariation1Values())):
                    new_value = form.get('vvalue-%s-%s' % (0, i))
                    new_values.append(new_value)
                self.context.getField('variation1_values').set(self.context, new_values)

            if len(var_config.getVariationAttributes()) >= 2:
                self.context.getField('variation2_attribute').set(self.context, vattr1)
                new_values = []
                for j in range(len(var_config.getVariation2Values())):
                    new_value = form.get('vvalue-%s-%s' % (1, j))
                    new_values.append(new_value)
                self.context.getField('variation2_values').set(self.context, new_values)


        # Make sure we had a proper form submit, not just a GET request
        submitted = form.get('form.submitted', False)
        if submitted:
            variation_config = IVariationConfig(self.context)
            edited_var_data = self._parse_edit_variations_form()
            variation_config.updateVariationConfig(edited_var_data)

            IStatusMessage(self.request).addStatusMessage(
                _(u'msg_variations_saved',
                  default=u"Variations saved."), type="info")
            self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.template()

    def _parse_edit_variations_form(self):
        """Parses the form the user submitted when editing variations,
        and returns a dictionary that contains the variation data.
        """
        form = self.request.form
        variation_config = IVariationConfig(self.context)
        variation_data = {}

        def _parse_data(variation_code):
            data = {}
            data['active'] = bool(form.get("%s-active" % variation_code))
            if data['active']:
                # TODO: Handle decimal more elegantly
                price = form.get("%s-price" % variation_code)
                try:
                    p = int(price)
                    # Create a tuple of ints from string
                    digits = tuple([int(i) for i in list(str(p))]) + (0, 0)
                    data['price'] = Decimal((0, digits, -2))
                except ValueError:
                    if not price == "":
                        data['price'] = Decimal(price)
                    else:
                        data['price'] = Decimal("0.00")

                data['skuCode'] = form.get("%s-skuCode" % variation_code)
                data['description'] = form.get("%s-description" % variation_code)

            # At this point the form has already been validated,
            # so uniqueness of sku codes is ensured
            data['hasUniqueSKU'] = True
            return data


        if len(variation_config.getVariationAttributes()) == 1:
            # One variation attribute
            for i, var1_value in enumerate(variation_config.getVariation1Values()):
                variation_code = 'var-%s' % i

                variation_data[variation_code] = _parse_data(variation_code)
        else:
            # Two variation attributes
            for i, var1_value in enumerate(variation_config.getVariation1Values()):
                for j, var2_value in enumerate(variation_config.getVariation2Values()):
                    variation_code = 'var-%s-%s' % (i, j)
                    variation_data[variation_code] = _parse_data(variation_code)

        return variation_data

    def getVariationsConfig(self):
        """Returns the variation config for the item being edited
        """
        context = aq_inner(self.context)
        variation_config = IVariationConfig(context)
        return variation_config


class MigrateVariationsView(BrowserView):
    """View to migrate variations of all shop items
    """

    def __call__(self):
        """Migrates all items
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        normalize = getUtility(IIDNormalizer).normalize
        response = ""
        stats = {}

        items = catalog(portal_type="ShopItem")
        for item in items:
            obj = item.getObject()
            stats[obj.UID()] = {'status': 'UNKNOWN',
                                'result': 'UNKNOWN'}
            var_conf = IVariationConfig(obj)

            # Skip broken OrderedDict items
            var_dict = var_conf.getVariationDict()
            if str(type(var_dict)) == "<class 'zc.dict.dict.OrderedDict'>":
                status = "SKIPPED: Broken OrderedDict Item '%s' at '%s'" % (obj.Title(), obj.absolute_url())
                response += status + "\n"
                print status
                stats[obj.UID()] = {'status': 'SKIPPED',
                                    'result': 'SUCCESS'}
                continue

            varAttrs = var_conf.getVariationAttributes()
            num_variations = len(varAttrs)
            if num_variations == 0:
                # No migration needed
                stats[obj.UID()] = {'status': 'NO_MIGRATION_NEEDED',
                                    'result': 'SUCCESS'}
                continue

            # Migrate items with 2 variations
            if num_variations == 2:
                migrated = True

                # Create mapping from old to new keys
                mapping = {}
                for i, v1 in enumerate(var_conf.getVariation1Values()):
                    for j, v2 in enumerate(var_conf.getVariation2Values()):
                        vkey = "%s-%s" % (normalize(v1), normalize(v2))
                        vcode = "var-%s-%s" % (i, j)
                        mapping[vkey] = vcode

                # Check if item needs to be migrated
                for key in var_dict.keys():
                    if key in mapping.keys():
                        migrated = False

                if migrated:
                    # Already migrated
                    stats[obj.UID()] = {'status': 'ALREADY_MIGRATED',
                                        'result': 'SUCCESS'}
                else:
                    # Migrate the item
                    print "Migrating %s..." % obj.Title()
                    for vkey in mapping.keys():
                        vcode = mapping[vkey]
                        try:
                            # Store data with new vcode
                            var_dict[vcode] = var_dict[vkey]
                            del var_dict[vkey]
                            var_conf.updateVariationConfig(var_dict)
                            transaction.commit()
                            stats[obj.UID()] = {'status': 'MIGRATED',
                                                'result': 'SUCCESS'}
                        except KeyError:
                            status = "FAILED: Migration of item '%s' at '%s' failed!" % (obj.Title(), obj.absolute_url())
                            response += status + "\n"
                            print status
                            stats[obj.UID()] = {'status': 'FAILED',
                                                'result': 'FAILED'}
                            break
                    if stats[obj.UID()]['status'] == 'MIGRATED':
                        status = "MIGRATED: Item '%s' at '%s'" %  (obj.Title(), obj.absolute_url())
                        response += status + "\n"
                        print status


            # Migrate items with 1 variation
            if num_variations == 1:
                migrated = True

                # Create mapping from old to new keys
                mapping = {}
                for i, v1 in enumerate(var_conf.getVariation1Values()):
                    vkey = normalize(v1)
                    vcode = "var-%s" % i
                    mapping[vkey] = vcode

                # Check if item needs to be migrated
                for key in var_dict.keys():
                    if key in mapping.keys():
                        migrated = False


                if migrated:
                    # Already migrated
                    stats[obj.UID()] = {'status': 'ALREADY_MIGRATED',
                                        'result': 'SUCCESS'}
                else:
                    # Migrate this item
                    print "Migrating %s..." % obj.Title()
                    for vkey in mapping.keys():
                        vcode = mapping[vkey]
                        try:
                            # Store data with new vcode
                            var_dict[vcode] = var_dict[vkey]
                            del var_dict[vkey]
                            var_conf.updateVariationConfig(var_dict)
                            transaction.commit()
                            stats[obj.UID()] = {'status': 'MIGRATED',
                                                'result': 'SUCCESS'}
                        except KeyError:
                            status = "FAILED: Migration of item '%s' at '%s' failed!" % (obj.Title(), obj.absolute_url())
                            response += status + "\n"
                            print status
                            stats[obj.UID()] = {'status': 'FAILED',
                                                'result': 'FAILED'}
                            break
                    if stats[obj.UID()]['status'] == 'MIGRATED':
                        status = "MIGRATED: Item '%s' at '%s'" %  (obj.Title(), obj.absolute_url())
                        response += status + "\n"
                        print status



        total = len(items)
        migrated = len([stats[k] for k in stats if stats[k]['status'] == 'MIGRATED'])
        skipped = len([stats[k] for k in stats if stats[k]['status'] == 'SKIPPED'])
        failed = len([stats[k] for k in stats if stats[k]['status'] == 'FAILED'])
        no_migration_needed = len([stats[k] for k in stats if stats[k]['status'] == 'NO_MIGRATION_NEEDED'])
        already = len([stats[k] for k in stats if stats[k]['status'] == 'ALREADY_MIGRATED'])

        summary = "TOTAL: %s   MIGRATED: %s   SKIPPED: %s   "\
                  "FAILED: %s   NO MIGRATION NEEDED: %s   ALREADY_MIGRATED: %s" % (total,
                                                                          migrated,
                                                                          skipped,
                                                                          failed,
                                                                          no_migration_needed,
                                                                          already)
        response = "%s\n\n%s" % (summary, response)
        return response
