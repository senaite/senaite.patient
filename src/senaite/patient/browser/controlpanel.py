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

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.patient import messageFactory as _
from zope import schema
from zope.interface import Interface


class IPatientControlPanel(Interface):
    """Controlpanel Settings
    """
    require_patient = schema.Bool(
        title=_(u"Require Patient"),
        description=_("Require Patients in Samples"),
        required=False,
        default=True,
    )

    patient_entry_mode = schema.Choice(
        title=_(u"Patient name entry mode"),
        description=_(u"Patient's name entry mode in Sample Add form"),
        source="senaite.patient.vocabularies.name_entry_modes",
        required=True,
        default="parts",
    )

    verify_temp_mrn = schema.Bool(
        title=_(u"Allow to verify samples with a temporary MRN"),
        description=_(u"If selected, users will be able to verify samples "
                      u"that have a Patient assigned with a temporary Medical "
                      u"Record Number (MRN)."),
        required=False,
        default=False,
    )

    publish_temp_mrn = schema.Bool(
        title=_(u"Allow to publish samples with a temporary MRN"),
        description=_(u"If selected, users will be able to publish samples "
                      u"that have a Patient assigned with a temporary Medical "
                      u"Record Number (MRN)."),
        required=False,
        default=False,
    )


class PatientControlPanelForm(RegistryEditForm):
    schema = IPatientControlPanel
    schema_prefix = "senaite.patient"
    label = _("SENAITE Patient Settings")


PatientControlPanelView = layout.wrap_form(
    PatientControlPanelForm, ControlPanelFormWrapper)
