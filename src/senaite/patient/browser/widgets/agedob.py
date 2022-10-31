# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
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

    def get_age_selected(self, context):
        name = self.getName()
        attr = "_%s_age_selected" % name
        return getattr(context, attr, False)

    def set_age_selected(self, context, value):
        name = self.getName()
        attr = "_%s_age_selected" % name
        setattr(context, attr, bool(value))

    def get_dob_estimated(self, context):
        name = self.getName()
        attr = "_%s_dob_estimated" % name
        return getattr(context, attr, self.get_age_selected(context))

    def set_dob_estimated(self, context, value):
        name = self.getName()
        attr = "_%s_dob_estimated" % name
        setattr(context, attr, bool(value))

    def get_current_age(self, dob):
        """Returns a dict with keys "years", "months", "days"
        """
        if not api.is_date(dob):
            return {}

        delta = patient_api.get_relative_delta(dob)
        return {
            "years": delta.years,
            "months": delta.months,
            "days": delta.days,
        }

    def is_age_supported(self, context):
        """Returns whether the introduction of age is supported or not
        """
        return patient_api.is_age_supported()

    def is_years_only(self, dob):
        """Returns whether months and days are not displayed when the age is
        greater than one year
        """
        if not patient_api.is_age_in_years():
            return False
        dob = self.get_current_age(dob)
        years = dob.get("years", 0)
        return years >= 1

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        value = form.get(field.getName())

        # Not interested in the hidden field, but in the age + dob specific
        if isinstance(value, (list, tuple)):
            value = value[0] or None

        # Allow non-required fields
        if not value:
            return None, {}

        # handle DateTime object when creating partitions
        if api.is_date(value):
            self.set_age_selected(instance, False)
            return value, {}

        # Grab the input for DoB first
        dob = value.get("dob", "")
        dob = patient_api.to_datetime(dob)
        age_selected = value.get("selector") == "age"

        # remember what was selected
        self.set_age_selected(instance, age_selected)

        # Maybe user entered age instead of DoB
        if age_selected:
            # Validate the age entered
            ymd = map(lambda p: value.get(p), ["years", "months", "days"])
            if not any(ymd):
                # No values set
                return None

            # Age in ymd format
            ymd = filter(lambda p: p[0], zip(ymd, 'ymd'))
            ymd = "".join(map(lambda p: "".join(p), ymd))

            # Calculate the DoB
            dob = patient_api.get_birth_date(ymd)

            # Consider DoB as estimated?
            orig_dob = value.get("original")
            orig_dob = patient_api.to_datetime(orig_dob)
            if not orig_dob:
                # First time age is set, assume dob is estimated
                self.set_dob_estimated(instance, True)
            else:
                # Do not update estimated unless value changed. Maybe the user
                # set the DoB at the beginning and now is just viewing the
                # Age value in edit mode. We do not want the property
                # "estimated" to change if he/she presses the Save button
                # without the dob value being changed
                if orig_dob.strftime("%y%m%d") != dob.strftime("%y%m%d"):
                    self.set_dob_estimated(instance, True)
        else:
            # User entered date of birth, so is not estimated
            self.set_dob_estimated(instance, False)

        return dob, {}


registerWidget(AgeDoBWidget, title="AgeDoBWidget")
