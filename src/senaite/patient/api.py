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

import re
from bika.lims import api
from bika.lims.utils import tmpID
from senaite.patient.config import PATIENT_CATALOG
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from dateutil.relativedelta import relativedelta
from datetime import datetime


_marker = object()


def is_patient_required():
    """Checks if the patient is required
    """
    required = api.get_registry_record(
        "senaite.patient.require_patient")
    if not required:
        return False
    return True


def get_patient_name_entry_mode():
    """Returns the entry mode for patient name
    """
    entry_mode = api.get_registry_record(
        "senaite.patient.patient_entry_mode")
    if not entry_mode:
        # Default to firstname + fullname
        entry_mode = "parts"
    return entry_mode


def get_patient_by_mrn(mrn, full_object=True, include_inactive=False):
    """Get a patient by Medical Record Number

    :param mrn: Unique medical record number
    :param full_object: If true, return objects instead of catalog brains
    :param include_inactive: Also find inactive patients
    :returns: Patient or None
    """
    query = {
        "portal_type": "Patient",
        "patient_mrn": api.safe_unicode(mrn).encode("utf8"),
        "is_active": True,
    }
    # Remove active index
    if include_inactive:
        query.pop("is_active", None)
    results = patient_search(query)
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
    """
    return api.get_tool(PATIENT_CATALOG)


def patient_search(query):
    """Search the patient catalog
    """
    catalog = get_patient_catalog()
    return catalog(query)


def create_temporary_patient():
    """Create a new temporary patient object

    :returns: temporary patient object
    """
    tid = tmpID()
    portal_type = "Patient"
    portal_types = api.get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)
    factory = getUtility(IFactory, fti.factory)
    patient = factory(tid)
    patient._setPortalTypeName(fti.getId())
    return patient


def safe_temporary_patient(patient):
    """Safe temporary patient to the patients folder
    """
    portal = api.get_portal()
    container = portal.patients
    notify(ObjectCreatedEvent(patient))
    container._setObject(patient.id, patient)
    patient = container.get(patient.getId())
    return patient


def update_patient(patient, **values):
    """Create a new patient
    """
    # set values explicitly
    patient.setMRN(values.get("mrn", api.get_id(patient)))
    patient.setPatientID(values.get("patient_id", ""))
    patient.setFirstname(values.get("firstname", ""))
    patient.setLastname(values.get("lastname", ""))
    patient.setGender(values.get("gender", ""))
    patient.setBirthdate(values.get("birthdate"))
    patient.setAddress(values.get("address"))
    # reindex the new values
    patient.reindexObject()


def to_datetime(date_value, default=None, tzinfo=None):
    if isinstance(date_value, datetime):
        return date_value

    # Get the DateTime
    date_value = api.to_date(date_value, default=None)
    if not date_value:
        if default is None:
            return None
        return to_datetime(default, tzinfo=tzinfo)

    # Convert to datetime and strip
    date_value = date_value.asdatetime()
    return date_value.replace(tzinfo=tzinfo)


def to_ymd(delta):
    """Returns a representation of a relative delta in ymd format
    """
    if not isinstance(delta, relativedelta):
        raise TypeError("delta parameter must be a relative_delta")

    ymd = list("ymd")
    diff = map(str, (delta.years, delta.months, delta.days))
    age = filter(lambda it: int(it[0]), zip(diff, ymd))
    return " ".join(map("".join, age))


def is_ymd(ymd):
    """Returns whether the string represents a period in ymd format
    """
    valid = map(lambda p: p in ymd, "ymd")
    return any(valid)


def get_birth_date(age_ymd, on_date=None):
    """Returns the birth date given an age in ymd format and the date when age
    was recorded or current datetime if None
    """
    on_date = to_datetime(on_date, default=datetime.now())

    def extract_period(val, period):
        num = re.findall(r'(\d{1,2})'+period, val) or [0]
        return api.to_int(num[0], default=0)

    # Extract the periods
    years = extract_period(age_ymd, "y")
    months = extract_period(age_ymd, "m")
    days = extract_period(age_ymd, "d")
    if not any([years, months, days]):
        raise AttributeError("No valid ymd: {}".format(age_ymd))

    dob = on_date - relativedelta(years=years, months=months, days=days)
    return dob


def get_age_ymd(birth_date, on_date=None):
    """Returns the age at on_date if not None. Otherwise, current age
    """
    delta = get_relative_delta(birth_date, on_date)
    return to_ymd(delta)


def get_relative_delta(from_date, to_date=None):
    """Returns the relative delta between two dates. If to_date is None,
    compares the from_date with now
    """
    from_date = to_datetime(from_date)
    if not from_date:
        raise TypeError("Type not supported: from_date")

    to_date = to_date or datetime.now()
    to_date = to_datetime(to_date)
    if not to_date:
        raise TypeError("Type not supported: to_date")

    return relativedelta(to_date, from_date)


def tuplify_identifiers(identifiers):
    """Convert identifiers to a list of key/value tuples

    :param identifiers: List of identifier dictionaries
    :returns: List of tuples
    """
    out = []
    for identifier in identifiers:
        key = identifier.get("key")
        value = identifier.get("value")
        out.append((key, value, ))
    return out


def to_identifier_type_name(identifier_type_key):
    """Convert an identifier type ID to the human readable name

    :param identifier_type_key: The keyword of the identifier
    :returns: Indetifiert type name
    """
    records = api.get_registry_record("senaite.patient.identifiers")

    name = identifier_type_key
    for record in records:
        key = record.get("key")
        if key != identifier_type_key:
            continue
        name = record.get("value")

    return name
