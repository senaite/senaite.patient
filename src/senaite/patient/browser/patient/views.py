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

import copy

from plone.dexterity.browser import edit
from senaite.core.browser.dexterity.add import DefaultAddForm
from senaite.core.browser.dexterity.add import DefaultAddView
from senaite.patient import messageFactory as _
from senaite.patient.api import is_patient_required


def fiddle_schema_fields(fields):
    """ Modify schema fields
    Code taken from:
    https://docs.plone.org/develop/plone/forms/z3c.form.html#making-widgets-required-conditionally
    """

    # We need to override the actual required from the
    # schema field which is a little tricky.
    # Schema fields are shared between instances
    # by default, so we need to create a copy of it
    if not is_patient_required():
        mrn = fields["mrn"]
        mrn_field = copy.copy(mrn.field)
        mrn_field.required = False
        mrn.field = mrn_field


class PatientAddForm(DefaultAddForm):
    """Patient edit view
    """
    portal_type = "Patient"
    default_fieldset_label = _("label_schema_personal", default=u"Personal")

    def updateFieldsFromSchemata(self):
        """see plone.autoform.base.AutoFields
        """
        super(PatientAddForm, self).updateFieldsFromSchemata()
        fiddle_schema_fields(self.fields)


class PatientAddView(DefaultAddView):
    form = PatientAddForm


class PatientEditForm(edit.DefaultEditForm):
    """Patient edit view
    """
    portal_type = "Patient"
    default_fieldset_label = _("label_schema_personal", default=u"Personal")

    def updateFieldsFromSchemata(self):
        """see plone.autoform.base.AutoFields
        """
        super(PatientEditForm, self).updateFieldsFromSchemata()
        fiddle_schema_fields(self.fields)
