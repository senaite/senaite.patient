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
# Copyright 2020-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.patient import logger
from senaite.patient.config import PRODUCT_NAME
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient.setuphandlers import setup_catalogs
from senaite.patient.catalog import PATIENT_CATALOG
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import get_indexes
from senaite.core.api.catalog import get_columns
from bika.lims import api

version = "1.1.0"

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
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    # https://github.com/senaite/senaite.patient/pull/14
    migrate_to_patient_catalog(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


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
