# -*- coding: utf-8 -*-

from bika.lims import api
from DateTime import DateTime
from senaite.patient import api as patient_api
from senaite.patient import logger


def on_object_created(instance, event):
    """Event handler when a sample was created
    """
    handle_age_and_birthdate(instance)
    update_patient(instance)


def on_object_edited(instance, event):
    """Event handler when a sample was edited
    """
    handle_age_and_birthdate(instance)
    update_patient(instance)


def handle_age_and_birthdate(instance):
    """Calculate Age from Birthdate and vice versa
    """
    now = DateTime()
    request = api.get_request()

    age_field = instance.getField("Age")
    dob_field = instance.getField("DateOfBirth")

    age = age_field.get(instance)
    dob = dob_field.get(instance)

    if dob:
        # calculate age
        yob = dob.year()
        age = now.year() - yob
        age_field.set(instance, age)
    elif age:
        # calculate date of birth
        current_year = now.year()
        yob = current_year - age
        dob = DateTime(yob, now.month(), now.day())
        dob_field.set(instance, dob)

    # update the request to display the values immediately
    request.set("Age", age)
    request.set("DateOfBirth", dob)


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
    gender = instance.getField("Gender").get(instance)
    birthdate = instance.getField("DateOfBirth").get(instance)
    age = instance.getField("Age").get(instance)
    address = instance.getField("PatientAddress").get(instance)
    fullname = instance.getField("PatientFullName").get(instance)

    return {
        "mrn": mrn,
        "age": age,
        "gender": gender,
        "birthdate": birthdate,
        "address": address,
        "fullname": fullname,
    }
