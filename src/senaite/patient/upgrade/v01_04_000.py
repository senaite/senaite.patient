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
from senaite.patient.api import patient_search
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import setup_catalogs

version = "1.4.0"
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


def upgrade_marital_status(tool):
    """Update controlpanel and add index to patient catalog

    :param tool: portal_setup tool
    """
    logger.info("Upgrade patient marital status ...")

    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    # import registry
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    # setup patient catalog
    setup_catalogs(portal)

    logger.info("Upgrade patient marital status [DONE]")


def upgrade_patient_mobile_phone_number(tool):
    """Move mobile phone -> additional_phone_numbers records

    :param tool: portal_setup tool
    """
    logger.info("Upgrade patient mobile number ...")

    patients = patient_search({"portal_type": "Patient"})

    for brain in patients:
        patient = api.get_object(brain)
        mobile = getattr(patient, "mobile", None)
        if not mobile:
            continue
        logger.info("Moving mobile phone '%s' -> additional_phone_numbers"
                    % mobile)
        numbers = patient.getAdditionalPhoneNumbers()
        numbers.append({"name": "Mobile", "phone": mobile})
        patient.setAdditionalPhoneNumbers(numbers)
        delattr(patient, mobile)

    logger.info("Upgrade patient mobile number [DONE]")
