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

from AccessControl import ClassSecurityInfo
from senaite.core.api import dtime
from Products.Archetypes.Registry import registerWidget
from senaite.core.browser.widgets import DateTimeWidget
from senaite.patient import api as patient_api


class AgeDoBWidget(DateTimeWidget):
    """A widget for the introduction of Age and/or Date of Birth.
    When Age is introduced, the Date of Birth is calculated automatically.
    """
    security = ClassSecurityInfo()
    _properties = DateTimeWidget._properties.copy()
    _properties.update({
        "show_time": False,
        "default_age": False,
        "macro": "senaite_patient_widgets/agedobwidget",
    })

    def is_age_supported(self):
        """Returns whether the introduction of age is supported or not
        """
        return patient_api.is_age_supported()

    def is_years_only(self):
        """Returns whether months and days are not displayed when the age is
        greater than one year
        """
        return patient_api.is_age_in_years()

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        value = form.get(field.getName())

        # Allow non-required fields
        if not value:
            return None, {}

        # We always return a dict suitable for the field
        output = dict.fromkeys(["dob", "from_age", "estimated"], False)

        if isinstance(value, (list, tuple)):
            # assume (dob, from_age, estimated)
            if not value:
                return None, {}
            output["dob"] = dtime.to_dt(value[0])
            output["from_age"] = value[1]
            output["estimated"] = value[2]
            return output, {}

        elif dtime.is_date(value):
            # handle date-like objects directly
            output["dob"] = dtime.to_dt(value)
            return output, {}

        elif patient_api.is_ymd(value):
            # handle age-like inputs directly
            output["dob"] = patient_api.get_birth_date(value)
            output["from_age"] = True
            return output, {}

        try:
            # We might get a ZPublisher.HTTPRequest.record
            value = dict(value)
        except ValueError:
            # value type is not supported
            return None, {}

        if value.get("selector") == "age":
            # Age entered
            ymd = map(lambda p: value.get(p), ["years", "months", "days"])
            if not any(ymd):
                # No values set
                return None, {}

            # Age in ymd format
            ymd = patient_api.to_ymd(ymd)

            # Calculate the DoB
            dob = patient_api.get_birth_date(ymd)
            output["dob"] = dob
            output["from_age"] = True

            # Consider DoB as estimated?
            orig_dob = value.get("original")
            orig_dob = dtime.to_dt(orig_dob)
            if not orig_dob:
                # First time age is set, assume dob is estimated
                output["estimated"] = True
            else:
                # Do not update estimated unless value changed. Maybe the user
                # set the DoB at the beginning and now is just viewing the
                # Age value in edit mode. We do not want the property
                # "estimated" to change if he/she presses the Save button
                # without the dob value being changed
                orig_ansi = dtime.to_ansi(orig_dob, show_time=False)
                dob_ansi = dtime.to_ansi(dob, show_time=False)
                output["estimated"] = orig_ansi != dob_ansi

        else:
            dob = value.get("dob", "")
            output["dob"] = dtime.to_dt(dob)
            output["from_age"] = value.get("from_age", False)
            output["estimated"] = value.get("estimated", False)

        return output, {}


registerWidget(AgeDoBWidget, title="AgeDoBWidget")
