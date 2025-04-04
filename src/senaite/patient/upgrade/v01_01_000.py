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
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core.api import dtime
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.config import PATIENT_CATALOG
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import setup_catalogs

version = "1.1.0"
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
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "controlpanel")
    setup.runImportStepFromProfile(profile, "plone.app.registry")
    setup.runImportStepFromProfile(profile, "workflow")

    # migrate addresses
    migrate_patient_addresses(portal)

    # fix non-unicode values
    fix_unicode_issues(portal)

    # add dateindex for birthdates
    setup_catalogs(portal)

    # migrate birthdates w/o time but with valid timezone
    migrate_birthdates(portal)

    # do not allow access to patients root folder other than lab personnel
    update_patient_folder_role_mappings(portal)

    # allow client-specific and local roles on patient objects
    update_patients_role_mappings(portal)

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def migrate_patient_addresses(portal):
    """Migrate patient addresses to new DX field
    """
    logger.info("Migrate patient addresses ...")
    catalog = api.get_tool(PATIENT_CATALOG)
    results = catalog({"portal_type": "Patient"})
    for brain in results:
        patient = api.get_object(brain)
        address = getattr(patient, "address", "")
        city = getattr(patient, "city", "")
        zipcode = getattr(patient, "zipcode", "")
        country = getattr(patient, "country", "")
        if any([address, city, zipcode, country]):
            value = {
                "type": "physical",
                "address": address,
                "city": city,
                "zip": zipcode,
                "country": country,
            }
            patient.setAddress(value)
    logger.info("Migrate patient addresses [DONE]")


def fix_unicode_issues(portal):
    """Ensure that field values from Patient objects are stored as unicode, and
    reindex catalogs to ensure the indexes contain encoded strings.
    To keep the safest convention, as with ATs:
      - field values are stored as unicode
      - accessors return encoded strings
      - catalog indexes store encoded strings
    """
    # Clear senaite_patient_catalog
    patient_catalog = api.get_tool(PATIENT_CATALOG)
    patient_catalog.manage_catalogClear()

    # Unindex getFullname index from portal_catalog
    portal_catalog = api.get_tool("portal_catalog")
    portal_catalog.clearIndex("getFullname")

    invalid = []

    # Walk through all Patients, reset the values to ensure the value is stored
    # as unicode and reindex them encoded (because of accessors)
    for patient in portal.patients.objectValues():
        # skip invalid patients
        # NOTE: This is obviously a bug in the data that should not happen!
        #       Anyhow, we we do not want this upgrade handler to fail on this
        #       and investigate elsewhere.
        if not patient.mrn:
            invalid.append(patient)
            continue
        patient.setEmail(patient.email)
        patient.setMRN(patient.mrn)
        try:
            patient.setPatientID(patient.patient_id)
        except ValueError:
            # flush duplicate IDs
            patient.setPatientID("")
        patient.setGender(patient.gender)
        patient.setFirstname(patient.firstname)
        patient.setLastname(patient.lastname)
        patient.reindexObject()

    # Reindex portal_catalog's getFullName index
    handler = ZLogHandler()
    portal_catalog.reindexIndex(["getFullname"], None, handler)

    if len(invalid) > 0:
        logger.error("Skipped %d patients w/o MRN set:" % len(invalid))
        for obj in invalid:
            logger.info("----> %s" % api.get_url(obj))


def migrate_birthdates(portal):
    """Migrate all birthdates from patients to be timezone aware
    """
    logger.info("Migrate patient birthdate timezones ...")
    catalog = api.get_tool(PATIENT_CATALOG)
    results = catalog({"portal_type": "Patient"})
    timezone = dtime.get_os_timezone()
    for brain in results:
        patient = api.get_object(brain)
        birthdate = patient.birthdate
        if birthdate:
            # clean existing time and timezone
            date = birthdate.strftime("%Y-%m-%d")
            # append current OS timezone if possible
            if timezone:
                date = date + " %s" % timezone
            patient.setBirthdate(date)
            patient.reindexObject()

    logger.info("Migrate patient birthdate timezones [DONE]")


def update_patient_folder_role_mappings(portal):
    """Updates the role mappings of patients root folder to prevent access to
    non-laboratory users
    """
    logger.info("Fixing permissions for patient's root folder ...")
    wf_tool = api.get_tool("portal_workflow")
    wf_id = "senaite_patient_folder_workflow"
    workflow = wf_tool.getWorkflowById(wf_id)
    folder = portal.patients
    workflow.updateRoleMappingsFor(folder)
    folder.reindexObjectSecurity()
    logger.info("Fixing permissions for patient's root folder [DONE]")


def update_patients_role_mappings(portal):
    """Updates the role mappings of patient objects to allow client-specific
    and local roles to have access
    """
    logger.info("Fixing permissions for patients ...")
    wf_tool = api.get_tool("portal_workflow")
    wf_id = "senaite_patient_workflow"
    workflow = wf_tool.getWorkflowById(wf_id)
    for patient in portal.patients.objectValues():
        workflow.updateRoleMappingsFor(patient)
        patient.reindexObjectSecurity()
    logger.info("Fixing permissions for patients [DONE]")
