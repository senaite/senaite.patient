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
# Copyright 2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import time

import transaction
from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.catalog_utilities import addZCTextIndex
from plone.registry.interfaces import IRegistry
from Products.DCWorkflow.Guard import Guard
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.patient import PRODUCT_NAME
from senaite.patient import PROFILE_ID
from senaite.patient import logger
from senaite.patient import permissions
from senaite.patient.config import PATIENT_CATALOG
from zope.component import getUtility

# Maximum threshold in seconds before a transaction.commit takes place
# Default: 300 (5 minutes)
MAX_SEC_THRESHOLD = 300

# Tuples of (type, [catalog])
CATALOGS_BY_TYPE = [
]

# Tuples of (catalog, index_name, index_type)
INDEXES = [
    (CATALOG_ANALYSIS_REQUEST_LISTING, "is_temporary_mrn", "BooleanIndex"),
    (CATALOG_ANALYSIS_REQUEST_LISTING, "medical_record_number", "KeywordIndex"),
    (PATIENT_CATALOG, "patient_mrn", "FieldIndex"),
    (PATIENT_CATALOG, "patient_email", "FieldIndex"),
    (PATIENT_CATALOG, "patient_fullname", "FieldIndex"),
    (PATIENT_CATALOG, "patient_searchable_text", "TextIndexNG3"),
]

# Tuples of (catalog, column_name)
COLUMNS = [
    (CATALOG_ANALYSIS_REQUEST_LISTING, "isMedicalRecordTemporary"),
    (PATIENT_CATALOG, "mrn"),
]

NAVTYPES = [
    "PatientFolder",
]

# An array of dicts. Each dict represents an ID formatting configuration
ID_FORMATTING = [
    {
        "portal_type": "Patient",
        "form": "P{seq:06d}",
        "prefix": "patient",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }, {
        "portal_type": "MedicalRecordNumber",
        "form": "TA{seq:06d}",
        "prefix": "medicalrecordnumber",
        "sequence_type": "generated",
        "split_length": 1,
    }
]

# Workflow updates
WORKFLOW_TO_UPDATE = {
    SAMPLE_WORKFLOW: {
        "states": {
            "verified": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditAge: (),
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMedicalRecordNumber: (),
                    permissions.FieldEditPatientAddress: (),
                    permissions.FieldEditPatientFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "published": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditAge: (),
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMedicalRecordNumber: (),
                    permissions.FieldEditPatientAddress: (),
                    permissions.FieldEditPatientFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "rejected": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditAge: (),
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMedicalRecordNumber: (),
                    permissions.FieldEditPatientAddress: (),
                    permissions.FieldEditPatientFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "invalid": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditAge: (),
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMedicalRecordNumber: (),
                    permissions.FieldEditPatientAddress: (),
                    permissions.FieldEditPatientFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "cancelled": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditAge: (),
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMedicalRecordNumber: (),
                    permissions.FieldEditPatientAddress: (),
                    permissions.FieldEditPatientFullName: (),
                    permissions.FieldEditGender: (),
                }
            }
        }
    }
}


def setup_handler(context):
    """Generic setup handler
    """
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    portal = context.getSite()

    # Setup patient content type
    add_patient_folder(portal)

    # Configure visible navigation items
    setup_navigation_types(portal)

    # Setup catalogs
    setup_catalogs(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    # Setup workflow (for field permissions mostly)
    setup_workflow(portal)

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def pre_install(portal_setup):
    """Runs before the first import step of the *default* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} pre-install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} pre-install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} uninstall handler [BEGIN]".format(PRODUCT_NAME.upper()))

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-{}:uninstall".format(PRODUCT_NAME)
    context = portal_setup._getImportContext(profile_id)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} uninstall handler [DONE]".format(PRODUCT_NAME.upper()))


def add_patient_folder(portal):
    """Adds the initial Patient folder
    """
    if portal.get("patients") is None:
        logger.info("Adding Patient Folder")
        portal.invokeFactory("PatientFolder", "patients", title="Patients")


def setup_navigation_types(portal):
    """Add additional types for navigation
    """
    registry = getUtility(IRegistry)
    key = "plone.displayed_types"
    display_types = registry.get(key, ())

    new_display_types = set(display_types)
    new_display_types.update(NAVTYPES)
    registry[key] = tuple(new_display_types)


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting
    """
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format_definition=formatting)
        logger.info("Setting up ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format_definition.get("portal_type", None)
    if not p_type:
        return

    form = format_definition.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in bs.getIDFormatting():
        if record.get('portal_type', '') == p_type:
            continue
        ids.append(record)
    ids.append(format_definition)
    bs.setIDFormatting(ids)


def setup_catalogs(portal):
    """Setup catalogs
    """
    logger.info("Setup Catalogs ...")

    # Setup catalogs by type
    logger.info("Setup Catalogs by type ...")
    for type_name, catalogs in CATALOGS_BY_TYPE:
        at = api.get_tool("archetype_tool")
        # get the current registered catalogs
        current_catalogs = at.getCatalogsByType(type_name)
        # get the desired catalogs this type should be in
        desired_catalogs = map(api.get_tool, catalogs)
        # check if the catalogs changed for this portal_type
        if set(desired_catalogs).difference(current_catalogs):
            # fetch the brains to reindex
            brains = api.search({"portal_type": type_name})
            # updated the catalogs
            at.setCatalogsByType(type_name, catalogs)
            logger.info("Assign '%s' type to Catalogs %s" %
                        (type_name, catalogs))
            for brain in brains:
                obj = api.get_object(brain)
                logger.info("Reindexing '%s'" % repr(obj))
                obj.reindexObject()

    # Setup catalog indexes
    logger.info("Setup indexes ...")
    to_index = {}
    for catalog, name, meta_type in INDEXES:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("Adding Index '%s' for field '%s' to catalog '%s"
                    % (meta_type, name, catalog))
        if meta_type == "ZCTextIndex":
            addZCTextIndex(c, name)
        else:
            c.addIndex(name, meta_type)

        if catalog not in to_index:
            to_index[catalog] = [name, ]
        else:
            to_index[catalog].append(name)

        logger.info("Added Index '%s' for field '%s' to catalog [DONE]"
                    % (meta_type, name))

    for catalog, names in to_index.items():
        start = time.time()
        logger.info("Indexing new index/es from {}: {} ..."
                    .format(catalog, ", ".join(names)))
        handler = ZLogHandler(steps=100)
        c = api.get_tool(catalog)
        c.reindexIndex(names, None, handler)
        end = time.time()
        if (end-start) > MAX_SEC_THRESHOLD:
            commit_transaction(portal)

    # Setup catalog metadata columns
    for catalog, name in COLUMNS:
        c = api.get_tool(catalog)
        if name not in c.schema():
            logger.info("Adding Column '%s' to catalog '%s' ..."
                        % (name, catalog))
            c.addColumn(name)
            logger.info("Added Column '%s' to catalog '%s' [DONE]"
                        % (name, catalog))
        else:
            logger.info("Column '%s' already in catalog '%s'  [SKIP]"
                        % (name, catalog))
            continue
    logger.info("Setup Catalogs [DONE]")


def commit_transaction(portal):
    start = time.time()
    logger.info("Commit transaction ...")
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s [DONE]"
                .format(end - start))


def setup_workflow(portal):
    """Setup workflow changes (status, transitions, permissions, etc.)
    """
    for wf_id, settings in WORKFLOW_TO_UPDATE.items():
        update_workflow(portal, wf_id, settings)


def update_workflow(portal, workflow_id, settings):
    """Updates the workflow with workflow_id with the settings passed-in
    """
    logger.info("Updating workflow '{}' ...".format(workflow_id))
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(workflow_id)
    if not workflow:
        logger.warn("Workflow '{}' not found [SKIP]".format(workflow_id))
    states = settings.get("states", {})
    for state_id, values in states.items():
        update_workflow_state(workflow, state_id, values)

    transitions = settings.get("transitions", {})
    for transition_id, values in transitions.items():
        update_workflow_transition(workflow, transition_id, values)


def update_workflow_state(workflow, status_id, settings):
    logger.info("Updating workflow '{}', status: '{}' ..."
                .format(workflow.id, status_id))

    # Create the status (if does not exist yet)
    new_status = workflow.states.get(status_id)
    if not new_status:
        workflow.states.addState(status_id)
        new_status = workflow.states.get(status_id)

    # Set basic info (title, description, etc.)
    new_status.title = settings.get("title", new_status.title)
    new_status.description = settings.get("description", new_status.description)

    # Set transitions
    trans = settings.get("transitions", ())
    if settings.get("preserve_transitions", False):
        trans = tuple(set(new_status.transitions+trans))
    new_status.transitions = trans

    # Set permissions
    update_workflow_state_permissions(workflow, new_status, settings)


def update_workflow_state_permissions(workflow, status, settings):
    # Copy permissions from another state?
    permissions_copy_from = settings.get("permissions_copy_from", None)
    if permissions_copy_from:
        logger.info("Copying permissions from '{}' to '{}' ..."
                    .format(permissions_copy_from, status.id))
        copy_from_state = workflow.states.get(permissions_copy_from)
        if not copy_from_state:
            logger.info("State '{}' not found [SKIP]".format(copy_from_state))
        else:
            for perm_id in copy_from_state.permissions:
                perm_info = copy_from_state.getPermissionInfo(perm_id)
                acquired = perm_info.get("acquired", 1)
                roles = perm_info.get("roles", acquired and [] or ())
                logger.info("Setting permission '{}' (acquired={}): '{}'"
                            .format(perm_id, repr(acquired), ', '.join(roles)))
                status.setPermission(perm_id, acquired, roles)

    # Override permissions
    logger.info("Overriding permissions for '{}' ...".format(status.id))
    state_permissions = settings.get('permissions', {})
    if not state_permissions:
        logger.info(
            "No permissions set for '{}' [SKIP]".format(status.id))
        return
    for permission_id, roles in state_permissions.items():
        state_roles = roles and roles or ()
        if isinstance(state_roles, tuple):
            acq = 0
        else:
            acq = 1
        logger.info("Setting permission '{}' (acquired={}): '{}'"
                    .format(permission_id, repr(acq),
                            ', '.join(state_roles)))
        # Check if this permission is defined globally for this workflow
        if permission_id not in workflow.permissions:
            workflow.permissions = workflow.permissions + (permission_id, )
        status.setPermission(permission_id, acq, state_roles)


def update_workflow_transition(workflow, transition_id, settings):
    logger.info("Updating workflow '{}', transition: '{}'"
                .format(workflow.id, transition_id))
    if transition_id not in workflow.transitions:
        workflow.transitions.addTransition(transition_id)
    transition = workflow.transitions.get(transition_id)
    transition.setProperties(
        title=settings.get("title"),
        new_state_id=settings.get("new_state"),
        after_script_name=settings.get("after_script", ""),
        actbox_name=settings.get("action", settings.get("title"))
    )
    guard = transition.guard or Guard()
    guard_props = {"guard_permissions": "",
                   "guard_roles": "",
                   "guard_expr": ""}
    guard_props = settings.get("guard", guard_props)
    guard.changeFromProperties(guard_props)
    transition.guard = guard
