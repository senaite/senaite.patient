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
from plone.registry.interfaces import IRegistry
from Products.DCWorkflow.Guard import Guard
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.setuphandlers import setup_other_catalogs
from senaite.core.workflow import SAMPLE_WORKFLOW
from senaite.patient import PRODUCT_NAME
from senaite.patient import logger
from senaite.patient import permissions
from senaite.patient.catalog.patient_catalog import PatientCatalog
from zope.component import getUtility

PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)

# Maximum threshold in seconds before a transaction.commit takes place
# Default: 300 (5 minutes)
MAX_SEC_THRESHOLD = 300

CATALOGS = (
    PatientCatalog,
)

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    (SAMPLE_CATALOG, "is_temporary_mrn", "", "BooleanIndex"),
    (SAMPLE_CATALOG, "medical_record_number", "", "KeywordIndex"),
]

# Tuples of (catalog, column_name)
COLUMNS = [
    (SAMPLE_CATALOG, "isMedicalRecordTemporary"),
    (SAMPLE_CATALOG, "getMedicalRecordNumberValue"),
    (SAMPLE_CATALOG, "getPatientFullName"),
    (SAMPLE_CATALOG, "getPatientID"),
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
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "published": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "dispatched": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "rejected": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "invalid": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
                    permissions.FieldEditGender: (),
                }
            },
            "cancelled": {
                "preserve_transitions": True,
                "permissions": {
                    # Field permissions (read-only)
                    permissions.FieldEditDateOfBirth: (),
                    permissions.FieldEditMRN: (),
                    permissions.FieldEditAddress: (),
                    permissions.FieldEditFullName: (),
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


def setup_catalogs(portal):
    """Setup patient catalogs
    """
    setup_core_catalogs(portal, catalog_classes=CATALOGS)
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)


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
