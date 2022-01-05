# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PATIENT.
#
# SENAITE.PATIENT is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2020-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction
from bika.lims import api
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import get_columns
from senaite.core.api.catalog import get_indexes
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.catalog import PATIENT_CATALOG
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.content.patient import Patient
from senaite.patient.setuphandlers import PROFILE_ID
from senaite.patient.setuphandlers import setup_catalogs

version = "1.0.0"

DELETE_INDEXES = (
    ("portal_catalog", "patient_mrn"),
    ("portal_catalog", "patient_email"),
    ("portal_catalog", "patient_fullname"),
    ("portal_catalog", "patient_searchable_text"),
)

DELETE_COLUMNS = (
    ("portal_catalog", "mrn"),
)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    # Allow/Disallow to verify/publish samples with temporary MRN
    setup.runImportStepFromProfile(PROFILE_ID, "plone.app.registry")
    # Update schema interface
    setup.runImportStepFromProfile(PROFILE_ID, "typeinfo")
    setup.runImportStepFromProfile(PROFILE_ID, "workflow")

    # https://github.com/senaite/senaite.patient/pull/24
    migrate_patient_item_to_container(portal)

    # https://github.com/senaite/senaite.patient/pull/14
    migrate_to_patient_catalog(portal)

    # Firstname + lastname instead of fullname
    fix_patients_fullname(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def migrate_patient_item_to_container(portal):
    """Migrate patient objects to be folderish

    Base class changed from Item -> Container

    https://community.plone.org/t/changing-dx-content-type-base-class-from-item-to-container
    http://blog.redturtle.it/2013/02/25/migrating-dexterity-items-to-dexterity-containers
    """
    logger.info("Migrate patients to be folderish ...")
    patients = portal.patients
    for patient in patients.objectValues():
        pid = patient.getId()
        patients._delOb(pid)
        patient.__class__ = Patient
        patients._setOb(pid, patient)
        BTreeFolder2Base._initBTrees(patients[pid])
        patients[pid].reindexObject()

    transaction.commit()
    logger.info("Migrate patients to be folderish [DONE]")


def migrate_to_patient_catalog(portal):
    """Migrate portal_catalog -> patient_catalog
    """
    logger.info("Migrate patient catalog...")

    # 1. Setup catalogs
    setup_catalogs(portal)

    # 2. Clean up indexes
    for catalog_id, idx_id in DELETE_INDEXES:
        catalog = api.get_tool(catalog_id)
        indexes = get_indexes(catalog)
        if idx_id in indexes:
            del_index(catalog, idx_id)
            logger.info("Deleted index '%s' from catalog '%s'"
                        % (idx_id, catalog_id))

    # 3. Clean up columns
    for catalog_id, column in DELETE_COLUMNS:
        catalog = api.get_tool(catalog_id)
        columns = get_columns(catalog)
        if column in columns:
            del_column(catalog, column)
            logger.info("Deleted column '%s' from catalog '%s'"
                        % (column, catalog_id))

    # 4. Reindex patient catalog
    patient_catalog = api.get_tool(PATIENT_CATALOG)
    patient_catalog.clearFindAndRebuild()

    logger.info("Migrate patient catalog [DONE]")


def fix_patients_fullname(portal):
    """Update the value of attribute 'firstname' with the value of 'fullname'
    """
    logger.info("Fixing patients full names ...")
    for patient in portal.patients.objectValues():
        if patient.get_firstname():
            # This one has the value set already
            continue

        raw = patient.__dict__
        firstname = raw.get("fullname", None)
        if firstname:
            patient.set_firstname(firstname)
            del(patient.__dict__["fullname"])
            patient.reindexObject()

    logger.info("Fixing patients full names ... [DONE]")
