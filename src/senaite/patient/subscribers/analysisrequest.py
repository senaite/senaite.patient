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
# Copyright 2020-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.behaviors import IClientShareableBehavior
from senaite.patient import api as patient_api
from senaite.patient import check_installed
from senaite.patient import logger
from senaite.patient import messageFactory as _


@check_installed(None)
def on_object_created(instance, event):
    """Event handler when a sample was created
    """
    patient = update_patient(instance)

    # no patient created when the MRN is temporary
    if not patient:
        return

    # append patient email to sample CC emails
    if patient.getEmailReport():
        email = patient.getEmail()
        add_cc_email(instance, email)

    # share patient with sample's client users if necessary
    reg_key = "senaite.patient.share_patients"
    if api.get_registry_record(reg_key, default=False):
        client_uid = api.get_uid(instance.getClient())
        behavior = IClientShareableBehavior(patient)
        # Note we get Raw clients because if current user is a Client, she/he
        # does not have enough privileges to wake-up clients other than the one
        # she/he belongs to. Still, we need to keep the rest of shared clients
        client_uids = behavior.getRawClients() or []
        if client_uid not in client_uids:
            client_uids.append(client_uid)
            behavior.setClients(client_uids)


@check_installed(None)
def on_object_edited(instance, event):
    """Event handler when a sample was edited
    """
    update_patient(instance)


def add_cc_email(sample, email):
    """add CC email recipient to sample
    """
    # get existing CC emails
    emails = sample.getCCEmails().split(",")
    # nothing to do
    if email in emails:
        return
    emails.append(email)
    # remove whitespaces
    emails = map(lambda e: e.strip(), emails)
    sample.setCCEmails(",".join(emails))


def update_patient(instance):
    if instance.isMedicalRecordTemporary():
        return
    mrn = instance.getMedicalRecordNumberValue()
    # Allow empty value when patients are not required for samples
    if mrn is None:
        return
    patient = patient_api.get_patient_by_mrn(mrn, include_inactive=True)
    # Create a new patient
    if patient is None:
        if patient_api.is_patient_allowed_in_client():
            # create the patient in the client
            container = instance.getClient()
        else:
            # create the patient in the global patients folder
            container = patient_api.get_patient_folder()
        # check if the user is allowed to add a new patient
        if not patient_api.is_patient_creation_allowed(container):
            logger.warn("User '{}' is not allowed to create patients in '{}'"
                        " -> setting MRN to temporary".format(
                            api.user.get_user_id(), api.get_path(container)))
            # make the MRN temporary
            # XXX: Refactor logic from Widget -> Field/DataManager
            mrn_field = instance.getField("MedicalRecordNumber")
            mrn = dict(mrn_field.get(instance))
            mrn["temporary"] = True
            mrn_field.set(instance, mrn)
            message = _("You are not allowed to add a patient in {} folder. "
                        "Medical Record Number set to Temporary."
                        .format(api.get_title(container)))
            instance.plone_utils.addPortalMessage(message, "error")
            return None

        logger.info("Creating new Patient in '{}' with MRN: '{}'"
                    .format(api.get_path(container), mrn))
        values = get_patient_fields(instance)
        try:
            patient = api.create(container, "Patient")
            patient_api.update_patient(patient, **values)
        except ValueError as exc:
            logger.error("%s" % exc)
            logger.error("Failed to create patient for values: %r" % values)
            raise exc
    return patient


def get_patient_fields(instance):
    """Extract the patient fields from the sample
    """
    mrn = instance.getMedicalRecordNumberValue()
    sex = instance.getField("Sex").get(instance)
    gender = instance.getField("Gender").get(instance)
    birthdate = instance.getField("DateOfBirth").get(instance)
    address = instance.getField("PatientAddress").get(instance)
    field = instance.getField("PatientFullName")
    firstname = field.get_firstname(instance)
    middlename = field.get_middlename(instance)
    lastname = field.get_lastname(instance)

    if address:
        address = {
            "type": "physical",
            "address": api.safe_unicode(address),
        }

    return {
        "mrn": mrn,
        "sex": sex,
        "gender": gender,
        "birthdate": birthdate[0],
        "address": address,
        "firstname": api.safe_unicode(firstname),
        "middlename": api.safe_unicode(middlename),
        "lastname": api.safe_unicode(lastname),
    }
