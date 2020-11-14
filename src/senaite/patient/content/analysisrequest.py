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

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.lims.browser.widgets import SelectionWidget
from bika.lims.fields import ExtDateTimeField
from bika.lims.fields import ExtIntegerField
from bika.lims.fields import ExtStringField
from bika.lims.interfaces import IAnalysisRequest
from senaite.patient import messageFactory as _
from senaite.patient.browser.widgets import TemporaryIdentifierWidget
from senaite.patient.content.fields import TemporaryIdentifierField
from senaite.patient.permissions import FieldEditAge
from senaite.patient.permissions import FieldEditDateOfBirth
from senaite.patient.permissions import FieldEditMedicalRecordNumber
from senaite.patient.permissions import FieldEditPatientAddress
from senaite.patient.permissions import FieldEditPatientFullName
from senaite.patient.permissions import FieldEditSex
from Products.Archetypes import DisplayList
from Products.Archetypes.Widget import IntegerWidget
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from senaite.core.browser.widgets import DateTimeWidget
from senaite.patient.interfaces import ISenaitePatientLayer
from zope.component import adapts
from zope.interface import implementer


SEX = DisplayList((
    ('male', _('Male')),
    ('female', _('Female')),
    ('unk', _(''))
    ))

MedicalRecordNumberField = TemporaryIdentifierField(
    "MedicalRecordNumber",
    required=True,
    validators=("temporary_identifier_validator",),
    read_permission=View,
    write_permission=FieldEditMedicalRecordNumber,
    widget=TemporaryIdentifierWidget(
        label=_("Medical Record #"),
        render_own_label=True,
        visible={
            'add': 'edit',
            'secondary': 'disabled',
            'header_table': 'prominent',
        },
    )
)

PatientFullNameField = ExtStringField(
    "PatientFullName",
    required=True,
    read_permission=View,
    write_permission=FieldEditPatientFullName,
    widget=StringWidget(
        label=_("Patient full name"),
        render_own_label=True,
        visible={
            'add': 'edit',
        }
    )
)

PatientAddressField = ExtStringField(
    "PatientAddress",
    read_permission=View,
    write_permission=FieldEditPatientAddress,
    widget=StringWidget(
        label=_("Place of residence"),
        render_own_label=True,
        visible={
            'add': 'edit',
        }
    )
)

DateOfBirthField = ExtDateTimeField(
    "DateOfBirth",
    required=False,
    read_permission=View,
    write_permission=FieldEditDateOfBirth,
    validators=("isDateFormat",),
    widget=DateTimeWidget(
        label=_("Date of birth"),
        datepicker_nofuture=1,
        render_own_label=True,
        visible={
            'add': 'edit',
        }
    ),
)

AgeField = ExtIntegerField(
    "Age",
    required=False,
    read_permission=View,
    write_permission=FieldEditAge,
    widget=IntegerWidget(
        label=_("Age"),
        render_own_label=True,
        visible={
            'add': 'edit',
        }
    ),
)

SexField = ExtStringField(
    "Sex",
    vocabulary=SEX,
    required=False,
    default="unk",
    read_permission=View,
    write_permission=FieldEditSex,
    widget=SelectionWidget(
        label=_("Sex"),
        format="select",
        visible={
            'add': 'edit',
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
            PatientFullNameField,
            PatientAddressField,
            DateOfBirthField,
            AgeField,
            SexField,
        ]
