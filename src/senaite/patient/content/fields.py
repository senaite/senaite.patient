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

import six
from AccessControl import ClassSecurityInfo
from bika.lims.fields import ExtensionField
from Products.Archetypes.Field import ObjectField
from senaite.patient import api as patient_api
from senaite.patient.browser.widgets import FullnameWidget
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

    def get(self, instance, **kwargs):
        val = super(FullnameField, self).get(instance, **kwargs)
        if isinstance(val, six.string_types):
            val = {"firstname": val, "lastname": ""}
        return val

    def get_firstname(self, instance):
        val = self.get(instance) or {}
        return val.get("firstname", "")

    def get_lastname(self, instance):
        val = self.get(instance) or {}
        return val.get("lastname", "")

    def get_fullname(self, instance):
        firstname = self.get_firstname(instance)
        lastname = self.get_lastname(instance)
        return " ".join(filter(None, [firstname, lastname]))
