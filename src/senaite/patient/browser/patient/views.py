# -*- coding: utf-8 -*-

import copy

from plone.dexterity.browser import add
from plone.dexterity.browser import edit
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


class PatientAddForm(add.DefaultAddForm):
    """Patient edit view
    """
    portal_type = "Patient"
    default_fieldset_label = _("label_schema_personal", default=u"Personal")

    def updateFieldsFromSchemata(self):
        """see plone.autoform.base.AutoFields
        """
        super(PatientAddForm, self).updateFieldsFromSchemata()
        fiddle_schema_fields(self.fields)


class PatientAddView(add.DefaultAddView):
    form = PatientAddForm

    def __init__(self, context, request, ti=None):
        super(PatientAddView, self).__init__(context, request, ti=ti)


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
