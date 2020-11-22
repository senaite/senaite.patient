# -*- coding: utf-8 -*-

from senaite.patient import api as patient_api
from senaite.patient import logger


def on_object_created(instance, event):
    """Event handler when a sample was created
    """
    mrn = instance.getMedicalRecordNumberValue()
    patient = patient_api.get_patient_by_mrn(mrn)
    if patient is None:
        logger.info("Creating new Patient with MRN #: {}".format(mrn))
        values = get_patient_fields(instance)
        patient_api.create_patient(mrn, **values)


def on_object_edited(instance, event):
    """Event handler when a sample was edited
    """
    mrn = instance.getMedicalRecordNumberValue()
    patient = patient_api.get_patient_by_mrn(mrn)
    if patient is None:
        logger.info("Creating new Patient with MRN #: {}".format(mrn))
        values = get_patient_fields(instance)
        patient_api.create_patient(mrn, **values)


def get_patient_fields(instance):
    """Extract the patient fields from the sample
    """
    age = instance.getField("Age").get(instance)
    gender = instance.getField("Gender").get(instance)
    birthdate = instance.getField("DateOfBirth").get(instance)
    address = instance.getField("PatientAddress").get(instance)
    fullname = instance.getField("PatientFullName").get(instance)

    return {
        "age": age,
        "gender": gender,
        "birthdate": birthdate,
        "address": address,
        "fullname": fullname,
    }
