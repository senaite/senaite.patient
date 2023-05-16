# -*- coding: utf-8 -*-

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

        # Not interested in the hidden field, but in the age + dob specific
        if isinstance(value, (list, tuple)):
            value = value[0] or None

        # Allow non-required fields
        if not value:
            return None, {}

        # We always return a dict suitable for the field
        output = dict.fromkeys(["dob", "from_age", "estimated"], False)

        if dtime.is_date(value):
            # handle date-like objects directly
            output["dob"] = dtime.to_dt(value)
            return output, {}

        elif patient_api.is_ymd(value):
            # handle age-like inputs directly
            output["dob"] = patient_api.get_birth_date(value)
            output["from_age"] = True
            return output, {}

        if value.get("selector") == "age":
            # Age entered
            ymd = map(lambda p: value.get(p), ["years", "months", "days"])
            if not any(ymd):
                # No values set
                return None, {}

            # Age in ymd format
            ymd = filter(lambda p: p[0], zip(ymd, 'ymd'))
            ymd = "".join(map(lambda p: "".join(p), ymd))

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
                dob_ansi = dob.to_ansi(dob, show_time=False)
                output["estimated"] = orig_ansi != dob_ansi

        else:
            # User entered date of birth, not estimated
            dob = value.get("dob", "")
            output["dob"] = dtime.to_dt(dob)

        return output, {}


registerWidget(AgeDoBWidget, title="AgeDoBWidget")
