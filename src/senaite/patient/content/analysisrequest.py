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

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.fields import ExtDateTimeField
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import IAnalysisRequest
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from senaite.patient import messageFactory as _
from senaite.patient.api import get_patient_name_entry_mode
from senaite.patient.api import is_patient_required
from senaite.patient.browser.widgets import AgeDoBWidget
from senaite.patient.browser.widgets import FullnameWidget
from senaite.patient.browser.widgets import TemporaryIdentifierWidget
from senaite.patient.config import GENDERS
from senaite.patient.content.fields import FullnameField
from senaite.patient.content.fields import TemporaryIdentifierField
from senaite.patient.interfaces import ISenaitePatientLayer
from senaite.patient.permissions import FieldEditAddress
from senaite.patient.permissions import FieldEditDateOfBirth
from senaite.patient.permissions import FieldEditFullName
from senaite.patient.permissions import FieldEditGender
from senaite.patient.permissions import FieldEditID
from senaite.patient.permissions import FieldEditMRN
from zope.component import adapts
from zope.interface import implementer

MAYBE_REQUIRED_FIELDS = [
    "MedicalRecordNumber",
    "PatientFullName",
]

MedicalRecordNumberField = TemporaryIdentifierField(
    "MedicalRecordNumber",
    required=True,
    validators=("temporary_identifier_validator",),
    read_permission=View,
    write_permission=FieldEditMRN,
    widget=TemporaryIdentifierWidget(
        label=_("Medical Record #"),
        render_own_label=True,
        visible={
            "add": "edit",
            "secondary": "disabled",
            "header_table": "prominent",
        },
    )
)

PatientIDField = ExtStringField(
    "PatientID",
    read_permission=View,
    write_permission=FieldEditID,
    widget=StringWidget(
        label=_("Patient ID"),
        render_own_label=True,
        visible={
            "add": "edit",
            "secondary": "disabled",
            "header_table": "prominent",
        }
    )
)

PatientFullNameField = FullnameField(
    "PatientFullName",
    required=True,
    read_permission=View,
    write_permission=FieldEditFullName,
    widget=FullnameWidget(
        label=_("Patient name"),
        entry_mode="parts",
        view_format="%(firstname)s %(lastname)s",
        render_own_label=True,
        visible={
            "add": "edit",
        }
    )
)

PatientAddressField = ExtStringField(
    "PatientAddress",
    read_permission=View,
    write_permission=FieldEditAddress,
    widget=StringWidget(
        label=_("Place of residence"),
        render_own_label=True,
        visible={
            "add": "edit",
        }
    )
)

DateOfBirthField = ExtDateTimeField(
    "DateOfBirth",
    required=False,
    read_permission=View,
    write_permission=FieldEditDateOfBirth,
    widget=AgeDoBWidget(
        label=_("Age / Date of birth"),
        render_own_label=True,
        default_age=True,
        show_time=False,
        datepicker_nofuture=True,
        visible={
            "add": "edit",
        }
    ),
)

GenderField = ExtStringField(
    "Gender",
    vocabulary=GENDERS,
    required=False,
    default="",
    read_permission=View,
    write_permission=FieldEditGender,
    widget=SelectionWidget(
        label=_("Gender"),
        format="select",
        visible={
            "add": "edit",
        }
    ),
)


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class AnalysisRequestSchemaExtender(object):
    """Extends the AnalysisRequest with additional fields
    """
    adapts(IAnalysisRequest)
    layer = ISenaitePatientLayer

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return [
            MedicalRecordNumberField,
            PatientIDField,
            PatientFullNameField,
            PatientAddressField,
            DateOfBirthField,
            GenderField,
        ]


@implementer(ISchemaModifier, IBrowserLayerAwareExtender)
class AnalysisRequestSchemaModifier(object):
    """Rearrange Schema Fields
    """
    adapts(IAnalysisRequest)
    layer = ISenaitePatientLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        required = is_patient_required()
        for fieldname in MAYBE_REQUIRED_FIELDS:
            field = schema.get(fieldname)
            field.required = required

        entry_mode = get_patient_name_entry_mode()
        fullname_field = schema.get("PatientFullName")
        fullname_field.widget.entry_mode = entry_mode
        return schema
