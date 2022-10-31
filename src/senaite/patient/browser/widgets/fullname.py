# -*- coding: utf-8 -*-

import six

from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget


class FullnameWidget(TypesWidget):
    """A widget for the introduction of person name, either fullname or the
    combination of firstname + lastname
    """
    security = ClassSecurityInfo()
    _properties = TypesWidget._properties.copy()
    _properties.update({
        "macro": "senaite_patient_widgets/fullnamewidget",
        "entry_mode": "parts",
        "view_format": "%(firstname)s %(middlename)s %(lastname)s",
        "size": "15",
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):

        value = form.get(field.getName())
        firstname = ""
        middlename = ""
        lastname = ""

        if isinstance(value, (list, tuple)):
            value = value[0] or None

        # handle string as fullname direct entry
        if isinstance(value, six.string_types):
            firstname = value.strip()

        elif value:
            firstname = value.get("firstname", "").strip()
            middlename = value.get("middlename", "").strip()
            lastname = value.get("lastname", "").strip()

        # Allow non-required fields
        if not any([firstname, lastname]):
            return None, {}

        output = {
            "firstname": firstname,
            "middlename": middlename,
            "lastname": lastname,
        }
        return output, {}


registerWidget(FullnameWidget, title="FullnameWidget")
