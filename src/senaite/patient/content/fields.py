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

import six
from AccessControl import ClassSecurityInfo
from bika.lims.fields import ExtensionField
from Products.Archetypes.Field import ObjectField
from senaite.patient.browser.widgets import TemporaryIdentifierWidget


class TemporaryIdentifierField(ExtensionField, ObjectField):
    """Field Extender of ObjectField that stores a dictionary with two keys:
    {'temporary': bool, 'value': str}, where 'temporary' indicates if the ID has
    to be considered as temporary or not, and 'value' actually represents the ID
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "temporaryidentifier",
        "default": {"temporary": False, "value": ""},
        "widget": TemporaryIdentifierWidget
    })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        val = super(TemporaryIdentifierField, self).get(instance, **kwargs)
        if isinstance(val, six.string_types):
            val = {"value": val}
        return val
