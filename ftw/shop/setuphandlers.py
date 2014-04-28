from Products.CMFCore.utils import getToolByName
import logging


# The profile id of our package:
PROFILE_ID = 'profile-ftw.shop:default'


class Empty:
    pass


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('ftw.shop')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    title_extras = Empty()

    # Specify the indexes you want, with ('index_name', 'index_type', extras)
    wanted = (('fullTitle', 'FieldIndex', title_extras),
              )

    indexables = []
    for name, meta_type, extras in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type, extras)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ftw_shop-default.txt') is None:
        return
    logger = context.getLogger('ftw.shop')
    site = context.getSite()
    add_catalog_indexes(site, logger)
