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

import six

from AccessControl import ClassSecurityInfo
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.Field import ObjectField
from senaite.core.api import dtime
from senaite.patient import api as patient_api
from senaite.patient.browser.widgets import AgeDoBWidget
from senaite.patient.browser.widgets import FullnameWidget
from senaite.patient.browser.widgets import TemporaryIdentifierWidget
from senaite.patient.config import AUTO_ID_MARKER
from senaite.patient.config import PATIENT_CATALOG
from senaite.patient.interfaces import IAgeDateOfBirthField
from zope.interface import implementer


class TemporaryIdentifierField(ExtensionField, ObjectField):
    """ObjectField extender that stores a dictionary with two keys:

        {
            'temporary': bool,  # flags the ID as temporary
            'value': str,       # current ID value
        }
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "temporaryidentifier",
        "default": {"temporary": False, "value": ""},
        "catalog": PATIENT_CATALOG,
        "auto_id_marker": AUTO_ID_MARKER,
        "widget": TemporaryIdentifierWidget
    })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        val = super(TemporaryIdentifierField, self).get(instance, **kwargs)
        if isinstance(val, six.string_types):
            val = {"value": val, "temporary": False}
        return val

    def get_linked_patient(self, instance):
        """Get the linked patient
        """
        mrn = instance.getMedicalRecordNumberValue()
        if not mrn:
            return None
        return patient_api.get_patient_by_mrn(mrn, include_inactive=True)


class FullnameField(ExtensionField, ObjectField):
    """ObjectField extender that stores a dictionary with two keys ('firstname'
    and 'lastname') that represent the fullname of a person
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "fullname",
        "default": None,
        "widget": FullnameWidget,
    })
    security = ClassSecurityInfo()

    def set(self, instance, value, **kwargs):
        val = dict.fromkeys(["firstname", "middlename", "lastname"], "")

        if isinstance(value, six.string_types):
            # Fullname entry mode
            val["firstname"] = value

        elif value is not None:
            # Ensure the stored object is from dict type. The received value
            # can be from ZPublisher record type and since the field inherits
            # from ObjectField, no conversion is done by the super field
            try:
                for key, value in value.items():
                    if key not in val:
                        continue
                    val[key] = value
            except AttributeError:
                msg = "Type not supported: {}".format(repr(type(value)))
                raise ValueError(msg)

        # Set default if no values for any of the keys
        values = filter(None, val.values())
        if not any(values):
            val = self.getDefault(instance)

        super(FullnameField, self).set(instance, val, **kwargs)

    def get_firstname(self, instance):
        val = self.get(instance) or {}
        return val.get("firstname", "")

    def get_middlename(self, instance):
        val = self.get(instance) or {}
        return val.get("middlename", "")

    def get_lastname(self, instance):
        val = self.get(instance) or {}
        return val.get("lastname", "")

    def get_fullname(self, instance):
        firstname = self.get_firstname(instance)
        middlename = self.get_middlename(instance)
        lastname = self.get_lastname(instance)
        return " ".join(filter(None, [firstname, middlename, lastname]))


@implementer(IAgeDateOfBirthField)
class AgeDateOfBirthField(ExtensionField, ObjectField):
    """ObjectField extender that stores a tuple (dob, from_age, estimated)
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "date_of_birth",
        "default": (None, False, False),
        "widget": AgeDoBWidget,
    })
    security = ClassSecurityInfo()

    def set(self, instance, value, **kwargs):

        dob, from_age, estimated = None, False, False

        def is_true(val):
            """Returns whether val evaluates to True
            """
            val = str(val).strip().lower()
            return val in ["y", "yes", "1", "true", "on"]

        if isinstance(value, (list, tuple)):
            # always assume (dob, from_age, estimated)
            dob = dtime.to_dt(value[0])
            from_age = is_true(value[1])
            estimated = is_true(value[2])

        elif isinstance(value, dict):
            from_age = is_true(value.get("from_age", False))
            estimated = is_true(value.get("estimated", False))

            # "dob" always has priority over "age"
            dob = value.get("dob")
            dob = dtime.to_dt(dob)
            if not dob:
                age = value.get("age")
                dob = patient_api.get_birth_date(age, default=None)
                # DoB is inferred from age, so it must be estimated,
                # regardless of what is coming with the dict
                from_age = dob is not None
                estimated = dob is not None

        elif dtime.is_date(value):
            dob = dtime.to_dt(value)
            from_age = is_true(kwargs.get("from_age", False))
            estimated = is_true(kwargs.get("estimated", False))

        elif patient_api.is_ymd(value):
            dob = patient_api.get_birth_date(value)
            from_age = estimated = True

        # if naive TZ, use system default's
        if dob and dtime.is_timezone_naive(dob):
            tz = dtime.get_os_timezone()
            dob = dtime.to_zone(dob, tz)

        # store the tuple or default
        val = (dob, from_age, estimated) if dob else self.getDefault(instance)
        super(AgeDateOfBirthField, self).set(instance, val)

    def get_date_of_birth(self, instance):
        """Returns whether the date of birth
        """
        return self.get(instance)[:][0]

    def get_age_ymd(self, instance, on_date=None):
        """Returns the age in ymd format at on_date or current date
        """
        age = self.get_age(instance, on_date=on_date)
        return patient_api.to_ymd(age, default=None)

    def get_age(self, instance, on_date=None):
        """Returns the age as a relative delta at on_date or current data
        """
        dob = self.get_date_of_birth(instance)
        try:
            return dtime.get_relative_delta(dob, on_date)
        except ValueError:
            return None

    def get_from_age(self, instance):
        """Returns whether the date of birth is calculated from age
        """
        return self.get(instance)[:][1]

    def get_estimated(self, instance):
        """Returns whether the date is estimated
        """
        return self.get(instance)[:][2]

    def get_max(self, instance):
        """Returns the max date allowed for date of birth
        """
        if patient_api.is_future_birthdate_allowed():
            return dtime.datetime.max
        return dtime.datetime.now()
