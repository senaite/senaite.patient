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
# Copyright 2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from datetime import datetime

import six
from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.fields import ExtensionField
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Field import StringField
from senaite.patient import api as patient_api
from senaite.patient.browser.widgets import AgeDoBWidget
from senaite.patient.browser.widgets import TemporaryIdentifierWidget
from senaite.patient.config import AUTO_ID_MARKER
from senaite.patient.config import PATIENT_CATALOG


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
        """Get the linked client
        """
        mrn = instance.getMedicalRecordNumberValue()
        if not mrn:
            return None
        return patient_api.get_patient_by_mrn(mrn, include_inactive=True)


class AgeDoBField(ExtensionField, StringField):
    """StringField extender that stores the Date of Birth in a YYYY-mm-dd
    format. An estimated date is represented as a partial date. For instance:
    '1979-12-07': Non-estimated DoB
    '1979-12': Estimated DoB (don't know exact day when it was born)
    '1979': Estimated DoB (don't know exact month and day when it was born)
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "agedob",
        "widget": AgeDoBWidget
    })

    def set(self, instance, value, **kwargs):

        if api.is_date(value):
            # Store in YYYY-mm-dd format
            value = value.strftime("%Y-%m-%d")

        elif isinstance(value, six.string_types):
            # Check if is a valid date
            parts = value.strip("-")
            parts.extend([0, 0, 0])
            year, month, day = parts[0:3]
            try:
                datetime(year, month or 1, day or 1)
            except ValueError as e:
                # Not a valid full/partial date
                raise AttributeError("{}: {}".format(str(e), value))

            parts = filter(None, parts)
            value = "-".join(parts)

        elif value:
            val_type = type(value)
            raise TypeError("Date or string expected, got {}".format(val_type))

        super(AgeDoBField, self).set(instance, value, **kwargs)
