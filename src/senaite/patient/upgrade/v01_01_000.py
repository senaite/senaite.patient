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

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.config import PATIENT_CATALOG
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import setup_catalogs

version = "1.1.0"


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

    # add dateindex for birthdates
    setup_catalogs(portal)

    # migrate birthdates w/o time but with valid timezone
    migrate_birthdates(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def migrate_birthdates(portal):
    """Migrate all birthdates from patients to be timezone aware
    """
    logger.info("Migrate patient birthdate timezones ...")
    catalog = api.get_tool(PATIENT_CATALOG)
    results = catalog({"portal_type": "Patient"})
    for brain in results:
        patient = api.get_object(brain)
        birthdate = patient.birthdate
        if birthdate:
            # clean existing time and timezone
            date = birthdate.strftime("%Y-%m-%d")
            patient.set_birthdate(date)

    logger.info("Migrate patient birthdate timezones [DONE]")
