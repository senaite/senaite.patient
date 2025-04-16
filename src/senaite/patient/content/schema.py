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

from plone.autoform import directives
from senaite.core.schema import PhoneField
from senaite.core.z3cform.widgets.phone import PhoneWidgetFactory
from senaite.patient import messageFactory as _
from zope import schema
from zope.interface import Interface


class IIdentifiersSchema(Interface):
    """Schema definition for identifiers field
    """
    key = schema.Choice(
        title=_(
            u"label_patient_identifiers_key",
            default=u"Type",
        ),
        description=_(
            u"description_patient_identifiers_key",
            default=u"The type of identifier that holds the ID",
        ),
        source="senaite.patient.vocabularies.identifiers",
        required=True,
    )

    value = schema.TextLine(
        title=_(
            u"label_patient_identifiers_value",
            default=u"ID",
        ),
        description=_(
            u"description_patient_identifiers_value",
            default=u"The identification number of the selected identifier",
        ),
        required=True,
    )


class IAdditionalEmailSchema(Interface):
    """Schema definition for additional emails field
    """
    name = schema.TextLine(
        title=_(
            u"label_patient_additional_emails_name",
            default="Name"
        ),
        description=_(
            u"description_patient_additional_emails_name",
            default=u"Private, Work, Other etc.",
        ),
        required=True,
    )

    email = schema.TextLine(
        title=_(
            u"label_patient_additional_emails_email",
            default=u"Email",
        ),
        description=_(
            u"description_patient_additional_emails_email",
            default=u"Email address"),
        required=True,
    )


class IAdditionalPhoneNumbersSchema(Interface):
    """Schema definition for additional phone numbers field
    """
    name = schema.TextLine(
        title=_(
            u"label_patient_additional_phone_numbers_name",
            default="Name",
        ),
        description=_(
            u"description_patient_additional_phone_numbers_name",
            default=u"Private, Work, Other etc."
        ),
        required=True,
    )

    directives.widget("phone", PhoneWidgetFactory)
    phone = PhoneField(
        title=_(
            u"label_patient_additional_phone_numbers_phone",
            default=u"Phone",
        ),
        description=_(
            u"description_patient_additional_phone_numbers_phone",
            default=u"Phone Number",
        ),
        required=True,
    )


class IRaceSchema(Interface):
    """Schema definition for patient race
    """
    race = schema.Choice(
        title=_(
            u"label_patient_race",
            default=u"Race",
        ),
        source="senaite.patient.vocabularies.races",
        required=False,
    )


class IEthnicitySchema(Interface):
    """Schema definition for patient ethnicity
    """
    ethnicity = schema.Choice(
        title=_(
            u"label_patient_ethnicity",
            default=u"Ethnicity",
        ),
        source="senaite.patient.vocabularies.ethnicities",
        required=False,
    )
