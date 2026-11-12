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
from bika.lims.interfaces import IRejected
from bika.lims.interfaces import IRetracted
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from senaite.core.behaviors import IClientShareableBehavior
from senaite.core.i18n import translate as t
from senaite.core.interfaces import ILockingState
from senaite.patient import api as patient_api
from senaite.patient import calc
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
    # update results ranges so dynamic specs are recalculated
    update_results_ranges(instance)
    # recalculate the results that use the patient data
    recalculate_results(instance)


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
            return None

        # refuse with a clear message instead of failing on creation, e.g.
        # when an import of the type information reset the client types
        if not patient_api.is_patient_type_allowed(container):
            title = api.get_title(container) or api.get_id(container)
            raise ValueError(
                "No patient found with MRN '{}' and patients cannot be "
                "created in '{}'. Please check the patient settings."
                .format(api.to_utf8(mrn), api.to_utf8(title)))

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
    dob_field = instance.getField("DateOfBirth")
    birthdate = dob_field.get_date_of_birth(instance)
    estimated = dob_field.get_estimated(instance)
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
        "birthdate": birthdate,
        "estimated_birthdate": estimated,
        "address": address,
        "firstname": api.safe_unicode(firstname),
        "middlename": api.safe_unicode(middlename),
        "lastname": api.safe_unicode(lastname),
    }


def update_results_ranges(sample):
    """Re-assigns the values of the results ranges for analyses, so dynamic
    specifications are re-calculated when patient values such as sex and date
    of birth are updated
    """
    # reset the result ranges so dynamic specs are grabbed again
    spec = sample.getSpecification()
    if spec:
        ranges = spec.getResultsRange()
        sample.setResultsRange(ranges, recursive=False)


def recalculate_results(sample):
    """Recalculates the results not yet verified whose calculation uses the
    patient data, together with the results that depend on them
    """
    # the analyses of a disposed or dispatched sample are locked
    if ILockingState.providedBy(sample):
        return
    analyses = sample.getAnalyses(full_objects=True)
    analyses = filter(uses_patient_data, analyses)
    recalculated = set()
    for analysis in analyses:
        recalculate_result(analysis, recalculated)


def uses_patient_data(analysis):
    """Returns whether the calculation of the analysis imports functions from
    `senaite.patient.calc`
    """
    imports = analysis.getCalculationImports()
    return any(imp.get("module") == calc.MODULE for imp in imports)


def recalculate_result(analysis, recalculated):
    """Recalculates the result of the analysis and of its dependents, as
    long as the result is not verified
    """
    uid = api.get_uid(analysis)
    if uid in recalculated:
        return
    recalculated.add(uid)
    if not is_recalculable(analysis):
        return
    previous = analysis.getFormattedResult(html=False)
    if analysis.calculateResult(override=True):
        if ISubmitted.providedBy(analysis):
            add_recalculation_remark(analysis, previous)
        analysis.reindexObject()
    for dependent in analysis.getDependents():
        recalculate_result(dependent, recalculated)


def add_recalculation_remark(analysis, previous):
    """Adds a remark to a submitted result that was recalculated

    The verifier would otherwise see the new result as if the analyst had
    submitted it. Nothing is added when the result did not change.
    """
    current = analysis.getFormattedResult(html=False)
    if current == previous:
        return
    remark = t(_(
        u"recalculated_after_patient_data_change",
        default=u"Recalculated after a change of the patient data: "
                u"${previous} -> ${current}",
        mapping={"previous": api.safe_unicode(previous),
                 "current": api.safe_unicode(current)}))
    remarks = api.safe_unicode(analysis.getRemarks() or u"")
    remarks = u"\n".join(filter(None, [remarks, remark]))
    analysis.setRemarks(remarks)


def is_recalculable(analysis):
    """Returns whether the result of the analysis can be recalculated: it is
    neither verified, nor retracted, rejected or cancelled
    """
    if IVerified.providedBy(analysis):
        return False
    if IRetracted.providedBy(analysis) or IRejected.providedBy(analysis):
        return False
    return api.is_active(analysis)
