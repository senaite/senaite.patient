# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.patient.config import PATIENT_CATALOG


def get_patient_by_mrn(mrn):
    """Get a patient by Medical Record Number
    """
    catalog = get_patient_catalog()
    query = {
        "portal_type": "Patient",
        "patient_mrn": mrn,
        "is_active": True,
    }
    results = catalog(query)
    count = len(results)
    if count == 0:
        return None
    elif count > 1:
        raise ValueError(
            "Found {} Patients for MRN {}".format(count, mrn))
    return api.get_object(results[0])


def get_patient_catalog():
    """Returns the patient catalog

    Currently `portal_catalog`
    """
    return api.get_tool(PATIENT_CATALOG)


def create_patient(mrn, **kw):
    """Create a new patient
    """
    portal = api.get_portal()
    patients = portal.patients
    patient = api.create(patients, "Patient")

    # set values explicitly
    patient.mrn = mrn
    patient.set_fullname(kw.get("fullname", ""))
    patient.set_age(api.to_int(kw.get("age"), None))
    patient.set_gender(kw.get("gender", ""))
    patient.set_birthdate(kw.get("birthdate"))
    patient.address = kw.get("address")
