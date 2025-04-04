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
# Copyright 2020-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import setup_catalog_mappings
from senaite.patient.setuphandlers import setup_catalogs

version = "1.5.0"
profile = "profile-{0}:default".format(PRODUCT_NAME)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def upgrade_catalog_indexes(tool):
    """Reinstall controlpanel registry

    :param tool: portal_setup tool
    """
    logger.info("Upgrade catalog indexes ...")
    portal = tool.aq_inner.aq_parent
    # setup patient catalog to add new indexes
    setup_catalogs(portal)
    logger.info("Upgrade catalog indexes [DONE]")


def import_registry(tool):
    """Imports the registry tool
    """
    logger.info("Reimport registry tool ...")
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    logger.info("Reimport registry tool [DONE]")


def update_catalog_mappings(tool):
    """Updates the catalog mappings of senaite registry
    """
    portal = tool.aq_inner.aq_parent
    setup_catalog_mappings(portal)
