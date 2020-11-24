# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.utils import tmpID
from senaite.patient.config import PATIENT_CATALOG
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


def get_patient_by_mrn(mrn, full_object=True, include_inactive=False):
    """Get a patient by Medical Record Number

    :param mrn: Unique medical record number
    :param full_object: If true, return objects instead of catalog brains
    :param include_inactive: Also find inactive patients
    :returns: Patient or None
    """
    catalog = get_patient_catalog()
    query = {
        "portal_type": "Patient",
        "patient_mrn": mrn,
        "is_active": True,
    }
    # Remove active index
    if include_inactive:
        query.pop("is_active", None)
    results = catalog(query)
    count = len(results)
    if count == 0:
        return None
    elif count > 1:
        raise ValueError(
            "Found {} Patients for MRN {}".format(count, mrn))
    if full_object is False:
        return results[0]
    return api.get_object(results[0])


def get_patient_catalog():
    """Returns the patient catalog

    Currently `portal_catalog`
    """
    return api.get_tool(PATIENT_CATALOG)


def create_empty_patient():
    """Create a new empty patient in the patients folder
    """
    tid = tmpID()
    portal = api.get_portal()
    container = portal.patients
    portal_type = "Patient"
    portal_types = api.get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    factory = getUtility(IFactory, fti.factory)
    obj = factory(tid)
    obj._setPortalTypeName(fti.getId())
    notify(ObjectCreatedEvent(obj))
    container._setObject(tid, obj)
    patient = container.get(obj.getId())
    return patient


def update_patient(patient, **values):
    """Create a new patient
    """
    # set values explicitly
    patient.set_mrn(values.get("mrn", api.get_id(patient)))
    patient.set_fullname(values.get("fullname", ""))
    patient.set_age(api.to_int(values.get("age"), None))
    patient.set_gender(values.get("gender", ""))
    patient.set_birthdate(values.get("birthdate"))
    patient.address = values.get("address")
    # reindex the new values
    patient.reindexObject()
