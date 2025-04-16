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

import transaction
from bika.lims import api
from bika.lims.api import snapshot
from bika.lims.interfaces import IAuditable
from bika.lims.interfaces import IDoNotSupportSnapshots
from bika.lims.workflow import isTransitionAllowed
from persistent.list import PersistentList
from plone import api as ploneapi
from senaite.core.api import dtime
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.p3compat import cmp
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import uncatalog_brain
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.api import patient_search
from senaite.patient.catalog import PATIENT_CATALOG
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import setup_catalogs
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from Products.ZCatalog.ProgressHandler import ZLogHandler

version = "1.4.0"
profile = "profile-{0}:default".format(PRODUCT_NAME)

PATIENT_WORKFLOW = "senaite_patient_workflow"
PATIENT_FOLDER_WORKFLOW = "senaite_patient_folder_workflow"
PATIENT_ID = "patient_id"
IDENTIFIERS = "senaite.patient.identifiers"

_marker = object()


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

        if isinstance(value, dict):
            # a dict already, do not update unless a key is missing
            keys = ["firstname", "middlename", "lastname"]
            exist = [key in value for key in keys]
            if all(exist):
                obj._p_deactivate()
                continue

        # set the field value
        try:
            field.set(obj, value)
        except ValueError:
            path = api.get_path(obj)
            logger.warn("No valid value for {}: {}".format(path, repr(value)))
            obj._p_deactivate()
            continue

        # reindex the object
        obj.reindexObject()

        # flush the object from memory
        obj._p_deactivate()

    logger.info("Fix samples without middle name [DONE]")


def allow_patients_in_clients(tool):
    """Allow to create patients inside clients
    """
    logger.info("Allow patients in clients ...")

    # import registry for controlpanel
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "plone.app.registry")

    logger.info("Allow patients in clients [DONE]")


@upgradestep(PRODUCT_NAME, version)
def update_patient_workflows(tool):
    """Update patient workflows and security settings
    """
    logger.info("Update patient workflows ...")

    # import rolemap, workflow and typeinfo
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")
    setup.runImportStepFromProfile(profile, "typeinfo")

    # get patient folder + workflow
    patientsfolder = portal.patients
    wf_tool = api.get_tool("portal_workflow")
    patients_workflow = wf_tool.getWorkflowById(PATIENT_FOLDER_WORKFLOW)

    # update rolemappings + object security for patients folder
    patients_workflow.updateRoleMappingsFor(patientsfolder)
    patientsfolder.reindexObject(idxs=["allowedRolesAndUsers"])

    # fetch patients + workflow
    patients = api.search({"portal_type": "Patient"}, PATIENT_CATALOG)
    total = len(patients)
    patient_workflow = wf_tool.getWorkflowById(PATIENT_WORKFLOW)

    for num, patient in enumerate(patients):
        obj = api.get_object(patient)
        logger.info("Processing patient %s/%s: %s"
                    % (num+1, total, obj.Title()))

        # update rolemappings + object security for patient
        patient_workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])

        if num and num % 10 == 0:
            logger.info("Commiting patient %s/%s" % (num+1, total))
            transaction.commit()
            logger.info("Commit done")

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Update patient workflows [DONE]")


@upgradestep(PRODUCT_NAME, version)
def migrate_patient_id_to_identifiers(tool):
    """Migrate Patient ID field to indentifiers
    """
    logger.info("Migrate patient ID to identifiers ...")

    # ensure PATIENT ID is in controlpanel records
    records = ploneapi.portal.get_registry_record(IDENTIFIERS, default=[])
    identifier_ids = map(lambda r: r.get("key"), records)
    if PATIENT_ID not in identifier_ids:
        records.append({
            "key": u"patient_id",
            "value": u"Patient ID",
        })
    ploneapi.portal.set_registry_record(IDENTIFIERS, value=records)

    query = {"portal_type": "Patient"}
    brains = api.search(query, PATIENT_CATALOG)
    total = len(brains)

    for num, brain in enumerate(brains):
        obj = api.get_object(brain)
        logger.info("Processing patient %s/%s: %s"
                    % (num+1, total, obj.getId()))

        value = getattr(obj, PATIENT_ID, _marker)
        if value is _marker:
            continue

        if api.is_string(value):
            patient_id = value
        elif isinstance(value, list):
            if len(filter(None, value)) > 0:
                patient_id = value[0]
        else:
            patient_id = ""

        delattr(obj, PATIENT_ID)

        if not patient_id:
            continue

        # patient ID already set
        if PATIENT_ID in obj.get_identifier_ids():
            continue

        # set Patient ID to identifiers
        identifiers = obj.getIdentifiers()
        identifiers.append({u"key": "patient_id", u"value": patient_id})
        obj.setIdentifiers(identifiers)

        logger.info("Migrated Patient ID %s to identifiers" % patient_id)

    logger.info("Migrate patient ID to identifiers [DONE]")


@upgradestep(PRODUCT_NAME, version)
def remove_stale_patient_id_catalog_entries(tool):
    """Remove stale Patient ID catalog entries
    """
    logger.info("Remove stale Patient ID catalog entries ...")

    # Patient Catalog
    del_index(PATIENT_CATALOG, "patient_id")
    del_index(PATIENT_CATALOG, "patient_searchable_id")
    del_column(PATIENT_CATALOG, "patient_id")

    # Sample Catalog
    del_column(SAMPLE_CATALOG, "getPatientID")

    logger.info("Remove stale Patient ID catalog entries [DONE]")


def migrate_date_of_birth_field(tool):
    """Resets the date of birth from samples
    """
    logger.info("Migrate DateOfBirth field to AgeDateOfBirthField ...")

    age_seleted_attr = "_AgeDoBWidget_age_selected"
    dob_estimated_attr = "_AgeDoBWidget_dob_estimated"

    uc = api.get_tool("uid_catalog")
    brains = uc(portal_type="AnalysisRequest")
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Migrated {0}/{1} fields".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        try:
            obj = api.get_object(brain)
        except AttributeError:
            uncatalog_brain(brain)
            continue

        # additional flags were saved as attributes
        age_selected = getattr(obj, age_seleted_attr, False),
        dob_estimated = getattr(obj, dob_estimated_attr, False)

        # remove them
        attrs = [age_seleted_attr, dob_estimated_attr]
        for attr in attrs:
            if hasattr(obj, attr):
                delattr(obj, attr)

        # New field expects a tuple (dob, from_age, estimated)
        field = obj.getField("DateOfBirth")
        value = field.get(obj)

        if dtime.is_date(value):
            value = (dtime.to_dt(value), age_selected, dob_estimated)
            field.set(obj, value)

        elif not isinstance(value, tuple):
            value = (None, False, False)
            field.set(obj, value)

        else:
            obj._p_deactivate()
            continue

        # reset date of birth value
        field.set(obj, value)

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Migrate DateOfBirth field to AgeDateOfBirthField [DONE]")


def update_naive_tz_dobs(tool):
    """Resets the date of birth from samples
    """
    logger.info("Updating timezone-naive dates of birth ...")

    uc = api.get_tool("uid_catalog")
    brains = uc(portal_type="AnalysisRequest")
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Migrated {0}/{1} fields".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        try:
            obj = api.get_object(brain)
        except AttributeError:
            uncatalog_brain(brain)
            continue

        # New field expects a tuple (dob, from_age, estimated)
        field = obj.getField("DateOfBirth")
        value = field.get(obj)
        dob = value[0] if value else None

        if dob and dtime.is_timezone_naive(dob):
            # re-set the value
            field.set(value)

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Updating timezone-naive dates of birth [DONE]")


def fix_mrn_duplicates(tool):
    """Fix duplicate MRNs
    """
    logger.info("Fixing duplicate MRNs ...")

    # Get the MRNs assigned to more than one Patient
    seen = {}
    duplicates = set()
    pt = api.get_tool(PATIENT_CATALOG)
    brains = pt(portal_type="Patient")
    for num, brain in enumerate(brains):
        mrn = brain.mrn
        if not mrn:
            continue
        if seen.get(mrn):
            duplicates.add(mrn)
        seen[mrn] = True

    # Fix duplicates
    map(fix_mrn_duplicate, duplicates)
    logger.info("Fixing duplicate MRNs [DONE]")


def fix_mrn_duplicate(mrn):
    """Fix Patients with same MRN as the one provided. Those that are active
    have priority to keep the MRN over those that are inactive. MRN is emptied
    and patient inactivated
    """
    logger.info("Fixing duplicates for {}".format(mrn))

    def sort_func(a, b):
        status_a = api.get_review_status(a)
        status_b = api.get_review_status(b)
        if status_a != status_b:
            # active before active
            return -1 if status_a == "active" else 1

        # same status, proritize by creation date
        created_a = api.get_creation_date(a)
        created_b = api.get_creation_date(b)
        return cmp(created_a, created_b)

    # do the search
    query = {"portal_catalog": "Patient", "patient_mrn": mrn}
    brains = api.search(query, PATIENT_CATALOG)
    if len(brains) < 2:
        logger.warn("No duplicates found for {}".format(mrn))
        return

    # sort by status and creation date
    patients = map(api.get_object, brains)
    patients = sorted(patients, cmp=sort_func)

    # clear mrn from objects, except from first one
    for patient in patients:
        # reset the mrn
        patient.mrn = u''
        # force transition
        action_id = "deactivate"
        if isTransitionAllowed(patient, action_id):
            api.do_transition_for(patient, "deactivate")
        patient.reindexObject()


def remove_patientfolder_snapshots(tool):
    """Removes the auditlog snapshots of Patient Folder and removes the
    IAuditable marker interface
    """
    logger.info("Removing snapshots from Patient Folder ...")
    portal = tool.aq_inner.aq_parent
    patients = portal.patients

    # do not take more snapshots
    alsoProvides(patients, IDoNotSupportSnapshots)

    # do not display audit log
    noLongerProvides(patients, IAuditable)

    # remove all snapshots except the first one (created)
    annotation = IAnnotations(patients)
    storage = annotation.get(snapshot.SNAPSHOT_STORAGE)
    if annotation and len(storage) > 0:
        annotation[snapshot.SNAPSHOT_STORAGE] = PersistentList([storage[0]])

    logger.info("Removing snapshots from Patient Folder [DONE]")


def allow_searches_by_patient_in_samples(tool):
    """Reindex the `listing_searchable_text` index from AnalysisRequest type
    so tokens with the patient name and mrn are added for searches
    """
    logger.info("Allowing searches by patient in samples ...")
    cat = api.get_tool(SAMPLE_CATALOG)
    cat.reindexIndex(["listing_searchable_text"], None, ZLogHandler())
    logger.info("Allowing searches by patient in samples [DONE]")


def remove_whitespaces_mrn(tool):
    """Resets the date of birth from samples
    """
    logger.info("Removing lead and trailing whitespaces from MRN ...")

    uc = api.get_tool("uid_catalog")
    brains = uc(portal_type="AnalysisRequest")
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Migrated {0}/{1} fields".format(num, total))

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        try:
            obj = api.get_object(brain)
        except AttributeError:
            uncatalog_brain(brain)
            continue

        if not obj:
            continue

        mrn = obj.getField("MedicalRecordNumber").get(obj)
        if not mrn:
            # Flush the object from memory
            obj._p_deactivate()
            continue

        value = mrn.get("value")
        if not value:
            # Flush the object from memory
            obj._p_deactivate()
            continue

        stripped = value.strip()
        if stripped == value:
            obj._p_deactivate()
            continue

        # Reset the value
        mrn["value"] = stripped
        obj.getField("MedicalRecordNumber").set(obj, mrn)
        # reindex so indexes and columns are updated in accordance
        obj.reindexObject()
        obj._p_deactivate()

    logger.info("Removing lead and trailing whitespaces from MRN [DONE]")
