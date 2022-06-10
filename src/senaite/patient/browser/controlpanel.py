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

import re

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.z3cform import layout
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.patient import messageFactory as _
from senaite.patient.api import patient_search
from senaite.patient.config import IDENTIFIERS
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_identifiers(context):
    return [{u"key": i[0], u"value": i[1]} for i in IDENTIFIERS]


class IIdentifier(Interface):
    key = schema.TextLine(
        title=_(u"Key"),
        description=_(
            u"The key will be stored in the database and must be unique"
        ),
        required=True,
    )

    value = schema.TextLine(
        title=_(u"Value"),
        description=_(
            u"The value will be displayed in the identifers selection"
        ),
        required=True,
    )


class IPatientControlPanel(Interface):
    """Controlpanel Settings
    """
    require_patient = schema.Bool(
        title=_(u"Require Patient"),
        description=_("Require Patients in Samples"),
        required=False,
        default=True,
    )

    directives.widget(
        "identifiers",
        DataGridWidgetFactory,
        auto_append=True)
    identifiers = schema.List(
        title=_(u"Identifiers"),
        description=_(
            u"List of identifiers that can be selected for a patient."
        ),
        value_type=DataGridRow(
            title=u"Identifier",
            schema=IIdentifier),
        required=False,
        defaultFactory=default_identifiers,
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

    share_patients = schema.Bool(
        title=_(u"Share patient on sample creation"),
        description=_(u"If selected, patients created or referred on sample "
                      u"creation will automatically be shared across users "
                      u"from same client the sample belongs to")
    )

    @invariant
    def validate_identifiers(data):
        """Checks if the keyword is unique and valid
        """
        keys = []
        for identifier in data.identifiers:
            key = identifier.get("key")
            # check if the key contains invalid characters
            if re.findall(r"[^A-Za-z\w\d\-\_]", key):
                raise Invalid(_("Key contains invalid characters"))
            # check if the key is unique
            if key in keys:
                raise Invalid(_("Key is not unique"))

            keys.append(key)

        # check if a used key is removed
        old_identifiers = data.__context__.identifiers
        old_keys = map(lambda i: i.get("key"), old_identifiers)
        removed = list(set(old_keys).difference(keys))

        if removed:
            # check if there are patients that use one of the removed keys
            brains = patient_search({"patient_identifier_keys": removed})
            if brains:
                raise Invalid(_("Can not delete identifiers that are in use"))


class PatientControlPanelForm(RegistryEditForm):
    schema = IPatientControlPanel
    schema_prefix = "senaite.patient"
    label = _("SENAITE Patient Settings")


PatientControlPanelView = layout.wrap_form(
    PatientControlPanelForm, ControlPanelFormWrapper)
