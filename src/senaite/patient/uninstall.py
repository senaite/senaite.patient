# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.api import delete
from plone.registry.interfaces import IRegistry
from Products.GenericSetup.utils import _resolveDottedName
from senaite.core.catalog import set_catalogs
from senaite.patient import logger
from senaite.patient import PRODUCT_NAME
from senaite.patient.setuphandlers import CATALOG_MAPPINGS
from senaite.patient.setuphandlers import CATALOGS
from senaite.patient.setuphandlers import COLUMNS
from senaite.patient.setuphandlers import INDEXES
from zope.component import getUtility

PROFILE_ID = "profile-{}:uninstall".format(PRODUCT_NAME)

TYPES_TO_REMOVE = ["Patient", "PatientFolder"]


def pre_uninstall(portal_setup):
    """Runs before the first import step of the *uninstall* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("%s pre-uninstall handler [BEGIN]" % PRODUCT_NAME.upper())

    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    # Purge product-specific types from navigation bar
    purge_navigation_types(portal)

    # Purge product-specific objects
    purge_objects(portal)

    # Purge product-specific catalogs, indexes and metadata
    purge_catalogs(portal)

    # Purge product-specific records from ID formatting
    purge_id_formatting(portal)

    logger.info("%s pre-uninstall handler [DONE]" % PRODUCT_NAME.upper())


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("%s post-uninstall handler [BEGIN]" % PRODUCT_NAME.upper())

    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("%s post-uninstall handler [DONE]" % PRODUCT_NAME.upper())


def purge_objects(portal):
    """Deletes objects that are specific of this product
    """
    logger.info("Deleting objects ...")

    # Delete patients folder and objects inside
    patients = portal.get("patients")
    if patients:
        logger.info("Removing folder: %s" % api.get_path(patients))
        delete(patients, check_permissions=False)

    # Delete patient objects left elsewhere (e.g in client folders)
    uc = api.get_tool("uid_catalog")
    brains = list(uc(portal_type=TYPES_TO_REMOVE))
    for brain in brains:
        try:
            obj = brain.getObject()
        except AttributeError:
            # Object does no longer exist, un-catalog the brain
            path = api.get_path(brain)
            # For DXs, uids of uid_catalog are absolute paths to portal root
            # see plone.app.referencablebehavior.uidcatalog
            logger.info("Removing stale brain: %s" % path)
            uc.uncatalog_object(path)
            continue

        # Delete the patient object
        path = api.get_path(obj)
        logger.info("Removing patient: %s" % path)
        delete(obj, check_permissions=False)

    logger.info("Deleting objects [DONE]")


def purge_catalogs(portal):
    """Uninstall catalogs, indexes and columns that are product-specific
    """
    logger.info("Uninstalling catalogs ...")

    # Delete product-specific indexes
    for index_info in INDEXES:
        cat_id = index_info[0]
        idx_name = index_info[1]
        cat = api.get_tool(cat_id)
        if idx_name in cat.indexes():
            logger.info("Removing index from %s: %s" % (cat.id, idx_name))
            cat.delIndex(idx_name)

    # Delete product-specific columns
    for cat_id, column in COLUMNS:
        cat = api.get_tool(cat_id)
        if column not in cat.schema():
            logger.info("Removing column from %s: %s" % (cat.id, column))
            cat.delColumn(column)

    # Delete product-specific catalogs
    for clazz in CATALOGS:
        module = _resolveDottedName(clazz.__module__)
        catalog_id = module.CATALOG_ID
        logger.info("Removing catalog: %s" % catalog_id)
        portal.manage_delObjects([catalog_id])

    # Clear catalog mappings
    for portal_type, catalogs in CATALOG_MAPPINGS:
        logger.info("Flushing catalog mappings for %s" % portal_type)
        set_catalogs(portal_type, tuple())

    logger.info("Uninstalling catalogs [DONE]")


def purge_id_formatting(portal):
    """Purges ID formatting records that are specific of this product
    """
    ids = ["Patient", "MedicalRecordNumber"]
    records = portal.bika_setup.getIDFormatting()
    records = filter(lambda rec: rec.get("portal_type") not in ids, records)
    portal.bika_setup.setIDFormatting(records)


def purge_navigation_types(portal):
    """Purges product-specific types from the navigation menu
    """
    key = "plone.displayed_types"
    registry = getUtility(IRegistry)
    to_display = registry.get(key, ())
    to_display = filter(lambda ty: ty not in TYPES_TO_REMOVE, to_display)
    registry[key] = tuple(to_display)
