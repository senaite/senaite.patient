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

import re
from datetime import datetime

from bika.lims import api
from bika.lims import deprecated
from dateutil.relativedelta import relativedelta
from senaite.core.api import dtime
from senaite.patient.config import PATIENT_CATALOG
from senaite.patient.permissions import AddPatient
from six import string_types

CLIENT_TYPE = "Client"
PATIENT_TYPE = "Patient"
CLIENT_VIEW_ID = "patients"
CLIENT_VIEW_ACTION = {
    "id": CLIENT_VIEW_ID,
    "name": "Patients",
    "action": "string:${object_url}/patients",
    "permission": "View",
    "category": "object",
    "visible": True,
    "icon_expr": "",
    "link_target": "",
    "condition": "",
}

YMD_REGEX = r'^((?P<y>(\d+))y){0,1}\s*' \
            r'((?P<m>(\d+))m){0,1}\s*' \
            r'((?P<d>(\d+))d){0,1}\s*'

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


def get_patient_address_format():
    """Returns the address format
    """
    address_format = api.get_registry_record(
        "senaite.patient.address_format")
    return address_format


def is_gender_visible():
    """Checks whether the gender is visible
    """
    key = "senaite.patient.gender_visible"
    return api.get_registry_record(key, default=True)


def is_future_birthdate_allowed():
    """Returns whether the introduction of a birth date in future is allowed
    """
    key = "senaite.patient.future_birthdate"
    return api.get_registry_record(key, default=False)


def is_age_supported():
    """Returns whether the introduction of age is supported
    """
    key = "senaite.patient.age_supported"
    return api.get_registry_record(key, default=True)


def is_age_in_years():
    """Returns whether the months and days should be omitted when displaying
    the age of a patient when is greater than one year
    """
    key = "senaite.patient.age_years"
    return api.get_registry_record(key, default=True)


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


def update_patient(patient, **values):
    """Create a new patient
    """
    # set values explicitly
    patient.setMRN(values.get("mrn", api.get_id(patient)))
    patient.setFirstname(values.get("firstname", ""))
    patient.setMiddlename(values.get("middlename", ""))
    patient.setLastname(values.get("lastname", ""))
    patient.setSex(values.get("sex", ""))
    patient.setGender(values.get("gender", ""))
    patient.setBirthdate(values.get("birthdate"))
    patient.setEstimatedBirthdate(values.get("estimated_birthdate", False))
    patient.setAddress(values.get("address"))
    # reindex the new values
    patient.reindexObject()


@deprecated("Use senaite.core.api.dtime.to_dt instead")
def to_datetime(date_value, default=None, tzinfo=None):
    if isinstance(date_value, datetime):
        return date_value

    # Get the DateTime
    date_value = dtime.to_DT(date_value)
    if not date_value:
        if default is None:
            return None
        return to_datetime(default, tzinfo=tzinfo)

    # Convert to datetime and strip
    date_value = date_value.asdatetime()
    return date_value.replace(tzinfo=tzinfo)


def to_ymd(period, default=_marker):
    """Returns the given period in ymd format

    If default is _marker, either a TypeError or ValueError is raised if
    the type of the period is not valid or cannot be converted to ymd format

    :param period: period to be converted to a ymd format
    :type period: str/relativedelta
    :param default: fall-back value to return as default
    :returns: a string that represents a period in ymd format
    :rtype: str
    """
    try:
        ymd_values = get_years_months_days(period)
    except (TypeError, ValueError) as e:
        if default is _marker:
            raise e
        return default

    # Return in ymd format, with zeros omitted
    ymd_values = map(str, ymd_values)
    ymd = filter(lambda it: int(it[0]), zip(ymd_values, "ymd"))
    ymd = " ".join(map("".join, ymd))

    # return a compliant ymd when no elapsed days
    return ymd or "0d"


def is_ymd(ymd):
    """Returns whether the string represents a period in ymd format

    :param ymd: supposedly ymd string to evaluate
    :type ymd: str
    :returns: True if a valid period in ymd format
    :rtype: bool
    """
    if not isinstance(ymd, string_types):
        return False
    try:
        get_years_months_days(ymd)
    except (TypeError, ValueError):
        return False
    return True


def get_years_months_days(period):
    """Returns a tuple of (years, months, days) given a period.

    Returns (0, 0, 0) if not possible to extract the years, months and days
    from the given period.

    :param period: period of time
    :type period: str/relativedelta/tuple/list
    :returns: a tuple with the years, months and days
    :rtype: tuple
    """
    if isinstance(period, relativedelta):
        return period.years, period.months, period.days

    if isinstance(period, (tuple, list)):
        years = api.to_int(period[0], default=0)
        months = api.to_int(period[1] if len(period) > 1 else 0, default=0)
        days = api.to_int(period[2] if len(period) > 2 else 0, default=0)
        return years, months, days

    if not isinstance(period, string_types):
        raise TypeError("{} is not supported".format(repr(period)))

    # to lowercase and remove leading and trailing spaces
    raw_ymd = period.lower().strip()

    # extract the years, months and days
    matches = re.search(YMD_REGEX, raw_ymd)
    values = [matches.group(v) for v in "ymd"]

    # if all values are None, assume the ymd format was not valid
    nones = [value is None for value in values]
    if all(nones):
        raise ValueError("Not a valid ymd: {}".format(repr(period)))

    # replace Nones with zeros and calculate everything with a relativedelta
    values = [api.to_int(value, 0) for value in values]
    delta = relativedelta(years=values[0], months=values[1], days=values[2])
    return get_years_months_days(delta)


def get_birth_date(period, on_date=None, default=_marker):
    """Returns the date when something started given a period in ymd format
    and the date when such period was recorded

    If on_date is None, uses current date time as the date from which the
    birth date is calculated.

    When ymd is not a valid period and default value is _marker, a TypeError
    or ValueError is raised. Otherwise, it returns the default value converted
    to datetime (or None if it cannot be converted)

    :param period: period of time
    :type period: str/relativedelta
    :param on_date: date from which the since date has to be calculated
    :type on_date: string/DateTime/datetime/date
    :param default: fall-back date-like value to return as default
    :returns: a tuple with the years, months and days
    :rtype: tuple
    """
    # extract the years, months and days from the period
    try:
        years, months, days = get_years_months_days(period)
    except (TypeError, ValueError) as e:
        if default is _marker:
            raise e
        return dtime.to_dt(default)

    # date when the ymd period was recorded
    on_date = dtime.to_dt(on_date)
    if not on_date:
        on_date = datetime.now()
        # apply system's current time zone
        tz = dtime.get_os_timezone()
        on_date = dtime.to_zone(on_date, tz)

    # calculate the date when everything started
    delta = relativedelta(years=years, months=months, days=days)
    return on_date - delta


def get_age_ymd(birth_date, on_date=None):
    """Returns the age at on_date if not None. Otherwise, current age
    """
    try:
        delta = dtime.get_relative_delta(birth_date, on_date)
        return to_ymd(delta)
    except (ValueError, TypeError):
        return None


@deprecated("Use senaite.core.api.dtime.get_relative_delta instead")
def get_relative_delta(from_date, to_date=None):
    """Returns the relative delta between two dates. If to_date is None,
    compares the from_date with now
    """
    return dtime.get_relative_delta(from_date, to_date)


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


def allow_patients_in_clients(allow=True):
    """Allow patient creation in patients
    """
    pt = api.get_tool("portal_types")
    # get the Client Type Info
    ti = pt.getTypeInfo(CLIENT_TYPE)
    # get the Client FTI
    fti = pt.get(CLIENT_TYPE)
    # get the current allowed types
    allowed_types = set(fti.allowed_content_types)
    # get the current actions
    action_ids = map(lambda a: a.id, ti._actions)

    # Enable / Disable Patient
    if allow:
        allowed_types.add(PATIENT_TYPE)
        if CLIENT_VIEW_ID not in action_ids:
            ti.addAction(**CLIENT_VIEW_ACTION)
            # move before contacts
            ref_index = action_ids.index("contacts")
            actions = ti._cloneActions()
            action = actions.pop()
            actions.insert(ref_index - 1, action)
            ti._actions = tuple(actions)
    else:
        allowed_types.discard(PATIENT_TYPE)
        if CLIENT_VIEW_ID in action_ids:
            ti.deleteActions([action_ids.index(CLIENT_VIEW_ID)])

    # set the new types
    fti.allowed_content_types = tuple(allowed_types)


def is_patient_allowed_in_client():
    """Returns wether patients can be created in clients or not
    """
    allowed = api.get_registry_record(
        "senaite.patient.allow_patients_in_clients", False)
    return allowed


def get_patient_folder():
    """Returns the global patient folder

    :returns: global patients folder
    """
    portal = api.get_portal()
    return portal.patients


def is_patient_creation_allowed(container):
    """Check if the security context allows to add a new patient

    :param container: The container to check the permission
    :returns: True if it is allowed to create a patient in the container,
              otherwise False
    """
    return api.security.check_permission(AddPatient, container)


def is_mrn_unique(mrn):
    """Checks whether the mrn provided is unique. This is, no patients with
    this mrn exist, regardless of their status

    :param mrn: The MRN to check its uniqueness
    :returns: True if no patient with this mrn exist
    """
    query = {
        "portal_type": "Patient",
        "patient_mrn": api.safe_unicode(mrn).encode("utf8"),
    }
    brains = api.search(query, PATIENT_CATALOG)
    return len(brains) == 0
