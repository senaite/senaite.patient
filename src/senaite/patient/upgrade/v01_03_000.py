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

from bika.lims import api
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.config import SEXES
from senaite.patient.setuphandlers import setup_catalogs

version = "1.3.0"
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
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")

    del_patients_action(portal)

    # Update the sex if possible
    update_patients_sex(portal)
    update_samples_sex(portal)

    setup_catalogs(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def del_patients_action(portal):
    logger.info("Removing patients action from inside patient type ...")
    type_info = portal.portal_types.getTypeInfo("Patient")
    action_id = "patients"
    actions = map(lambda action: action.id, type_info._actions)
    if action_id in actions:
        index = actions.index(action_id)
        type_info.deleteActions([index])
    logger.info("Removing patients action from inside patient type [DONE]")


def update_patients_sex(portal):
    logger.info("Updating sex for patients without Sex assigned ...")
    for patient in portal.patients.objectValues():
        # Update the sex if necessary
        update_sex_with_gender(patient)

        # Flush the object from memory
        patient._p_deactivate()

    logger.info("Updating sex for patients without Sex assigned [DONE]")


def update_samples_sex(portal):
    logger.info("Updating sex for samples without Sex assigned ...")
    query = {"portal_type": "AnalysisRequest"}
    brains = api.search(query, SAMPLE_CATALOG)
    for brain in brains:
        sample = api.get_object(brain)
        update_sex_with_gender(sample)

        # Flush the object from memory
        sample._p_deactivate()

    logger.info("Updating sex for samples without Sex assigned [DONE]")


def update_sex_with_gender(obj):
    if obj.getSex():
        # Sex is set already, do nothing
        return

    sexes = dict(SEXES).keys()
    gender = obj.getGender()
    if gender not in sexes:
        return

    obj.setSex(gender)
