# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.patient import api as patient_api
from senaite.patient import check_installed
from senaite.patient import logger


@check_installed(None)
def on_object_created(instance, event):
    """Event handler when a sample was created
    """
    update_patient(instance)


@check_installed(None)
def on_object_edited(instance, event):
    """Event handler when a sample was edited
    """
    # XXX "save" from Sample's header view does not call widget's process_form
    request = api.get_request()
    field_name = "DateOfBirth"
    if field_name in request.form:
        dob_field = instance.getField(field_name)
        dob = dob_field.widget.process_form(instance, dob_field, request.form)
        if dob is not None:
            dob_field.set(instance, dob[0])

    update_patient(instance)


def update_patient(instance):
    if instance.isMedicalRecordTemporary():
        return
    mrn = instance.getMedicalRecordNumberValue()
    # Allow empty value when patients are not required for samples
    if mrn is None:
        return
    patient = patient_api.get_patient_by_mrn(mrn, include_inactive=True)
    if patient is None:
        logger.info("Creating new Patient with MRN #: {}".format(mrn))
        patient = patient_api.create_empty_patient()
        # XXX: Sync the values back from Sample -> Patient?
        values = get_patient_fields(instance)
        patient_api.update_patient(patient, **values)


def get_patient_fields(instance):
    """Extract the patient fields from the sample
    """
    mrn = instance.getMedicalRecordNumberValue()
    patient_id = instance.getField("PatientID").get(instance)
    gender = instance.getField("Gender").get(instance)
    birthdate = instance.getField("DateOfBirth").get(instance)
    address = instance.getField("PatientAddress").get(instance)
    field = instance.getField("PatientFullName")
    firstname = field.get_firstname(instance)
    lastname = field.get_lastname(instance)

    return {
        "mrn": mrn,
        "patient_id": patient_id,
        "gender": gender,
        "birthdate": birthdate,
        "address": address,
        "firstname": firstname,
        "lastname": lastname,
    }
