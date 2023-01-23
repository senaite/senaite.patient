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

import six
import transaction

from bika.lims import api
from senaite.core.catalog import SAMPLE_CATALOG
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
        delattr(patient, "mobile")

    logger.info("Upgrade patient mobile number [DONE]")


def upgrade_patient_control_panel(tool):
    """Reinstall controlpanel registry

    :param tool: portal_setup tool
    """
    logger.info("Upgrade patient control panel ...")
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "actions")
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    setup.runImportStepFromProfile(profile, "controlpanel")
    logger.info("Upgrade patient control panel [DONE]")


def upgrade_catalog_indexes(tool):
    """Reinstall controlpanel registry

    :param tool: portal_setup tool
    """
    logger.info("Upgrade catalog indexes ...")
    portal = tool.aq_inner.aq_parent
    # setup patient catalog to add new indexes
    setup_catalogs(portal)
    logger.info("Upgrade catalog indexes [DONE]")


def fix_samples_middlename(tool):
    """Reindex samples with a patient middle name set so the metadata
    getPatientFullName gets populated correctly and therefore, and displayed
    in samples listing as well
    """
    logger.info("Fix samples middle name ...")
    query = {"portal_type": "AnalysisRequest"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num > 0 and num % 100 == 0:
            logger.info("Fix samples middle name: {}/{}".format(num, total))

        obj = api.get_object(brain)
        brain_fullname = brain.getPatientFullName
        try:
            obj_fullname = obj.getPatientFullName()
            reindex = obj_fullname != brain_fullname
        except AttributeError:
            # AttributeError: 'unicode' object has no attribute 'get'
            # Value is not stored as a dict. These cases are handled by 1406
            reindex = False

        if reindex:
            obj.reindexObject()

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Fix samples middle name [DONE]")


def fix_samples_without_middlename(tool):
    """Walks through registered samples and sets an empty middlename to those
    that do not have a middle name set
    """
    logger.info("Fix samples without middle name ...")
    query = {"portal_type": "AnalysisRequest"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Processed objects: {}/{}".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        obj = api.get_object(brain)
        field = obj.getField("PatientFullName")
        value = field.get(obj)
        if value is None:
            obj._p_deactivate()
            continue

        if isinstance(value, six.string_types):
            # old instance with the fullname stored as str
            value = {"firstname": value}

        if not isinstance(value, dict):
            # found some ZPublisher records!!
            # (Pdb++) type(value)
            # <class 'ZPublisher.HTTPRequest.record'>
            try:
                value = dict(value)
            except:
                str_type = repr(type(value))
                logger.error("Type not supported: {}".format(str_type))
                obj._p_deactivate()
                continue

        # Do not update unless a key is missing
        keys = ["firstname", "middlename", "lastname"]
        exist = filter(lambda key: key in value, keys)
        if len(exist) == len(keys):
            obj._p_deactivate()
            continue

        # set the field value
        field.set(obj, value)

        # reindex the object
        obj.reindexObject()

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Fix samples without middle name [DONE]")
