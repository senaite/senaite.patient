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
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.patient import messageFactory as _
from senaite.patient.api import patient_search
from senaite.patient.config import ETHNICITIES
from senaite.patient.config import IDENTIFIERS
from senaite.patient.config import RACES
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_identifiers(context):
    return [{u"key": i[0], u"value": i[1]} for i in IDENTIFIERS]


@provider(IContextAwareDefaultFactory)
def default_races(context):
    return [{u"key": i[0], u"value": i[1]} for i in RACES]


@provider(IContextAwareDefaultFactory)
def default_ethnicities(context):
    return [{u"key": i[0], u"value": i[1]} for i in ETHNICITIES]


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


class IRace(Interface):
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
            u"The value will be displayed in the race selection"
        ),
        required=True,
    )


class IEthnicity(Interface):
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
            u"The value will be displayed in the ethnicity selection"
        ),
        required=True,
    )


class IPatientControlPanel(Interface):
    """Controlpanel Settings
    """

    ###
    # Fieldsets
    ###
    model.fieldset(
        "patient_field_settings",
        label=_(u"Field Settings"),
        description=_(""),
        fields=[
            "patient_entry_mode",
            "age_supported",
            "age_years",
            "gender_visible",
        ],
    )

    model.fieldset(
        "patient_identifiers",
        label=_(u"Identifiers"),
        description=_(""),
        fields=[
            "identifiers",
        ],
    )

    model.fieldset(
        "patient_race_ethnicity",
        label=_(u"Race and Ethnicity"),
        description=_(""),
        fields=[
            "races",
            "ethnicities",
        ],
    )

    model.fieldset(
        "patient_sharing",
        label=_(u"Sharing"),
        description=_(""),
        fields=[
            "share_patients",
        ],
    )

    ###
    # Fields
    ###
    require_patient = schema.Bool(
        title=_(u"Require Medical Record Number (MRN)"),
        description=_(
            u"Make the MRN field mandatory in Sample Add form"
        ),
        required=False,
        default=True,
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

    show_icon_temp_mrn = schema.Bool(
        title=_(u"Display an alert icon on samples with a temporary MRN"),
        description=_(
            u"When selected, an alert icon is displayed in samples listing for "
            u"samples that have a Patient assigned with a temporary Medical "
            u"Record Number (MRN)."
        ),
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

    gender_visible = schema.Bool(
        title=_(u"Gender identity"),
        description=_(
            u"If selected, a field for the introduction of the patient's "
            u"gender identity becomes visible in Sample registration form and "
            u"view. The field for birth sex is always visible regardless of "
            u"this setting."
        ),
        required=False,
        default=True,
    )

    age_supported = schema.Bool(
        title=_(u"Age introduction"),
        description=_(
            u"If selected, a control for the introduction of either the age or "
            u"date of birth will be displayed in Sample registration form and "
            u"view. Otherwise, only the control for the introduction of the "
            u"date of birth will be displayed"
        ),
        required=False,
        default=True,
    )

    age_years = schema.Bool(
        title=_(
            u"label_controlpanel_patient_ageyears",
            default=u"Age in years"),
        description=_(
            u"description_controlpanel_patient_ageyears",
            default=u"If selected, months and days won't be displayed in "
                    u"sample view if the age of the patient is greater than "
                    u"one year. In such case, only years will be displayed"
        ),
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

    directives.widget(
        "races",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    races = schema.List(
        title=_(
            u"label_controlpanel_patient_races",
            default=u"Races"),
        description=_(
            u"description_controlpanel_patient_races",
            default=u"Patient race categories"
        ),
        value_type=DataGridRow(schema=IRace),
        required=True,
        defaultFactory=default_races,
    )

    directives.widget(
        "ethnicities",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    ethnicities = schema.List(
        title=_(
            u"label_controlpanel_patient_ethnicities",
            default=u"Ethnicities"),
        description=_(
            u"description_controlpanel_patient_ethnicities",
            default=u"Patient ethnicity categories"
        ),
        value_type=DataGridRow(schema=IEthnicity),
        required=True,
        defaultFactory=default_ethnicities,
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

    @invariant
    def validate_races(data):
        """Checks if the keyword is unique and valid
        """
        keys = []
        for race in data.races:
            key = race.get("key")
            # check if the key contains invalid characters
            if re.findall(r"[^A-Za-z\w\d\-\_]", key):
                raise Invalid(_("Key contains invalid characters"))
            # check if the key is unique
            if key in keys:
                raise Invalid(_("Key '%s' is not unique" % key))

            keys.append(key)

        # check if a used key is removed
        old_races = data.__context__.races
        old_keys = map(lambda i: i.get("key"), old_races)
        removed = list(set(old_keys).difference(keys))

        if removed:
            # check if there are patients that use one of the removed keys
            brains = patient_search({"patient_race_keys": removed})
            if brains:
                raise Invalid(_("Can not delete races that are in use"))

    @invariant
    def validate_ethnicities(data):
        """Checks if the keyword is unique and valid
        """
        keys = []
        for ethnicity in data.ethnicities:
            key = ethnicity.get("key")
            # check if the key contains invalid characters
            if re.findall(r"[^A-Za-z\w\d\-\_]", key):
                raise Invalid(_("Key contains invalid characters"))
            # check if the key is unique
            if key in keys:
                raise Invalid(_("Key '%s' is not unique" % key))

            keys.append(key)

        # check if a used key is removed
        old_ethnicities = data.__context__.ethnicities
        old_keys = map(lambda i: i.get("key"), old_ethnicities)
        removed = list(set(old_keys).difference(keys))

        if removed:
            # check if there are patients that use one of the removed keys
            brains = patient_search({"patient_ethnicity_keys": removed})
            if brains:
                raise Invalid(_("Can not delete ethnicities that are in use"))


class PatientControlPanelForm(RegistryEditForm):
    schema = IPatientControlPanel
    schema_prefix = "senaite.patient"
    label = _("Patient Settings")
    description = _("Global settings for patients")


PatientControlPanelView = layout.wrap_form(
    PatientControlPanelForm, ControlPanelFormWrapper)
