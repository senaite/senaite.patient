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

from string import Template

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.api.mail import is_valid_email_address
from datetime import datetime
from plone.autoform import directives
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from Products.CMFCore import permissions
from senaite.core.api import dtime
from senaite.core.behaviors import IClientShareable
from senaite.core.content.base import Container
from senaite.core.schema import AddressField
from senaite.core.schema import DatetimeField
from senaite.core.schema import PhoneField
from senaite.core.schema.addressfield import OTHER_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.datetimewidget import DatetimeWidget
from senaite.core.z3cform.widgets.phone import PhoneWidgetFactory
from senaite.patient import api as patient_api
from senaite.patient import messageFactory as _
from senaite.patient.catalog import PATIENT_CATALOG
from senaite.patient.config import GENDERS
from senaite.patient.config import SEXES
from senaite.patient.i18n import translate
from senaite.patient.interfaces import IPatient
from six import string_types
from z3c.form.interfaces import NO_VALUE
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant

from .schema import IAdditionalEmailSchema
from .schema import IAdditionalPhoneNumbersSchema
from .schema import IEthnicitySchema
from .schema import IIdentifiersSchema
from .schema import IRaceSchema

POSSIBLE_ADDRESSES = [OTHER_ADDRESS, PHYSICAL_ADDRESS, POSTAL_ADDRESS]


def get_max_birthdate(context=None):
    """Returns the max date for date of birth
    """
    if patient_api.is_future_birthdate_allowed():
        return dtime.datetime.max
    return dtime.datetime.now()


class IPatientSchema(model.Schema):
    """Patient Content
    """

    directives.omitted("title")
    title = schema.TextLine(
        title=u"Title",
        required=False
    )

    directives.omitted("description")
    description = schema.Text(
        title=u"Description",
        required=False
    )

    # race/ethnicity fieldset
    fieldset(
        "race_and_ethnicity",
        label=u"Race and Ethnicity",
        fields=["races", "ethnicities"])

    # contact fieldset
    fieldset(
        "email_and_phone",
        label=u"Email and Phone",
        fields=[
            "email",
            "additional_emails",
            "phone",
            "additional_phone_numbers",
        ])

    # address fieldset
    fieldset(
        "address",
        label=u"Address",
        fields=["address"])

    # Default

    mrn = schema.TextLine(
        title=_(u"label_patient_mrn", default=u"Medical Record #"),
        description=_(u"Patient Medical Record Number"),
        required=True,
    )

    directives.widget(
        "identifiers",
        DataGridWidgetFactory,
        auto_append=True)
    identifiers = DataGridField(
        title=_(u"Patient Identifiers"),
        description=_(
            u"Define one or more identifers for this patient"
        ),
        value_type=DataGridRow(
            title=u"Identifier",
            schema=IIdentifiersSchema),
        required=False,
        missing_value=[],
        default=[],
    )

    email_report = schema.Bool(
        title=_(
            u"label_patient_email_report",
            default=u"Email results report"),
        description=_(
            u"Add the patient email as CC recipient to new samples"),
        required=False,
        default=False,
    )

    firstname = schema.TextLine(
        title=_(u"label_patient_firstname", default=u"Firstname"),
        description=_(u"Patient firstname"),
        required=False,
    )

    middlename = schema.TextLine(
        title=_(u"label_patient_middlename", default=u"Middlename"),
        description=_(u"Patient middlename"),
        required=False,
    )

    lastname = schema.TextLine(
        title=_(u"label_patient_lastname", default=u"Lastname"),
        description=_(u"Patient lastname"),
        required=False,
    )

    sex = schema.Choice(
        title=_(u"label_patient_sex", default=u"Sex"),
        description=_(u"Patient sex at birth"),
        source="senaite.patient.vocabularies.sex",
        default="",
        required=True,
    )

    gender = schema.Choice(
        title=_(u"label_patient_gender", default=u"Gender Identity"),
        description=_(u"Patient gender identity"),
        source="senaite.patient.vocabularies.gender",
        default="",
        required=True,
    )

    marital_status = schema.Choice(
        title=_(u"label_patient_marital_status", default=u"Marital Status"),
        description=_(u"Patient legally defined marital status"),
        source="senaite.patient.vocabularies.marital_statuses",
        default="UNK",
        required=True,
    )

    directives.widget(
        "races",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    races = DataGridField(
        title=_(u"label_patient_races", default=u"Races"),
        description=_(
            "description_patient_races",
            default=u"General race category reported by the patient "
            u"- subject may have more than one"
        ),
        value_type=DataGridRow(schema=IRaceSchema),
        required=False,
        missing_value=[],
        default=[],
    )

    directives.widget(
        "ethnicities",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    ethnicities = DataGridField(
        title=_(u"label_patient_ethnicities", default=u"Ethnicities"),
        description=_(
            "description_patient_ethnicities",
            default=u"General ethnicity category reported by the patient "
            u"- subject may have more than one"
        ),
        value_type=DataGridRow(schema=IEthnicitySchema),
        required=False,
        missing_value=[],
        default=[],
    )

    # Contact

    # primary patient email address
    email = schema.TextLine(
        title=_(
            u"label_primary_patient_email",
            default=u"Primary Email Address"
        ),
        description=_(
            u"description_patient_primary_email",
            default=u"Primary email address for this patient"),
        required=False,
    )

    # additional emails
    directives.widget(
        "additional_emails",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    additional_emails = DataGridField(
        title=_(
            u"label_patient_additional_emails",
            default=u"Additional Email Addresses"),
        description=_(
            u"description_patient_additional_emails",
            default=u"Additional email addresses for this patient"
        ),
        value_type=DataGridRow(
            title=u"Email",
            schema=IAdditionalEmailSchema),
        required=False,
        missing_value=[],
        default=[],
    )

    # primary phone number
    directives.widget("phone", PhoneWidgetFactory)
    phone = PhoneField(
        title=_(
            u"label_patient_primary_phone",
            default=u"Primary Phone Number",),
        description=_(
            u"description_patient_primary_phone",
            u"Primary phone number for this patient"),
        required=False,
    )

    # additional phone numbers
    directives.widget(
        "additional_phone_numbers",
        DataGridWidgetFactory,
        allow_reorder=True,
        auto_append=True)
    additional_phone_numbers = DataGridField(
        title=_(u"label_patient_additional_phone_numbers",
                default=u"Additional Phone Numbers"),
        description=_(
            u"description_patient_additional_phone_numbers",
            u"Additional phone numbers for this patient"),
        value_type=DataGridRow(
            title=u"Phone",
            schema=IAdditionalPhoneNumbersSchema),
        required=False,
        missing_value=[],
        default=[],
    )

    # Address
    address = AddressField(
        title=_("Address"),
        address_types=[
            PHYSICAL_ADDRESS,
            POSTAL_ADDRESS,
            OTHER_ADDRESS,
        ]
    )

    directives.widget("birthdate",
                      DatetimeWidget,
                      show_time=False)
    birthdate = DatetimeField(
        title=_(u"label_patient_birthdate", default=u"Birthdate"),
        description=_(u"Patient birthdate"),
        required=False,
    )
    # XXX core's DateTimeWidget relies on field's get_max function if not 'max'
    #     property is explicitly set to the widget
    birthdate.get_max = get_max_birthdate

    estimated_birthdate = schema.Bool(
        title=_(
            u"label_patient_estimated_birthdate",
            default=u"Birthdate is estimated"
        ),
        description=_(
            u"description_patient_estimated_birthdate",
            default=u"Select this option if the patient's date of birth is "
                    u"estimated"
        ),
        default=False,
        required=False,
    )

    deceased = schema.Bool(
        title=_(
            u"label_patient_deceased",
            default=u"Deceased"),
        description=_(
            u"description_patient_deceased",
            default=u"Select this option if the patient is deceased"),
        required=False,
        default=False,
    )

    @invariant
    def validate_mrn(data):
        """Checks if the patient MRN # is unique
        """
        # https://community.plone.org/t/dexterity-unique-field-validation
        context = getattr(data, "__context__", None)
        if context is not None:
            if context.mrn == data.mrn:
                # nothing changed
                return

        empty = not data.mrn
        required = patient_api.is_patient_required()

        if empty and required:
            raise Invalid(
                _("invalid_patient_mrn_is_required",
                  default="Patient Medical Record Number is required"))

        elif empty:
            return

        # search for uniqueness
        if not patient_api.is_mrn_unique(data.mrn):
            raise Invalid(
                _("invalid_patient_mrn_must_be_unique",
                  default="Patient Medical Record Number must be unique"))

    @invariant
    def validate_email_report(data):
        """Checks if an email is set
        """
        value = data.email_report
        if not value:
            return

        # check if a valid email is in the request
        # Note: Workaround for missing `data.email`
        request = api.get_request()
        email = request.form.get("form.widgets.email")
        if email and is_valid_email_address(email):
            return

        # mark the request to avoid multiple raising
        key = "_v_email_report_checked"
        if getattr(request, key, False):
            return
        setattr(request, key, True)
        raise Invalid(_("Please set a valid email address first"))

    @invariant
    def validate_email(data):
        """Checks if the email is correct
        """
        if not data.email:
            return
        if not is_valid_email_address(data.email):
            raise Invalid(_("Patient email is invalid"))

    @invariant
    def validate_additional_emails(data):
        """Checks if the additional emails are valid
        """
        if not data.additional_emails:
            return
        for record in data.additional_emails:
            if record == NO_VALUE:
                continue
            email = record.get("email")
            if email and not is_valid_email_address(email):
                raise Invalid(_("Email address %s is invalid" % email))

    @invariant
    def validate_birthdate(data):
        """Checks if birthdate is in the past
        """
        if not data.birthdate:
            return

        # check if field is in current fieldset to avoid multiple raising
        if 'birthdate' not in data._Data_data___:
            return

        if patient_api.is_future_birthdate_allowed():
            return

        # comparison must be tz-aware
        tz = dtime.get_os_timezone()
        dob = dtime.to_zone(data.birthdate, tz)
        now = dtime.to_zone(datetime.now(), tz)
        if now < dob:
            raise Invalid(_("Date of birth cannot be a future date"))


@implementer(IPatient, IPatientSchema, IClientShareable)
class Patient(Container):
    """Results Interpretation Template content
    """

    # XXX Remove after 1.5.0
    #     See https://github.com/senaite/senaite.patient/pull/119
    _catalogs = [PATIENT_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def Title(self):
        return self.getFullname()

    @security.protected(permissions.View)
    def getMRN(self):
        """Returns the MRN with the field accessor
        """
        accessor = self.accessor("mrn")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMRN(self, value):
        """Set MRN by the field accessor
        """
        # XXX These checks will be quite common on setters linked to `required`
        # fields. We could add a decorator or, if we use our own implementation
        # of BaseField, take this into consideration in the `get(self)` func.
        if not value:
            raise ValueError("Value is missing or empty")

        if not isinstance(value, string_types):
            raise ValueError("Type is not supported: {}".format(repr(value)))

        value = value.strip()
        accessor = self.accessor("mrn")
        if accessor(self) == api.safe_unicode(value):
            # Value has not changed
            return

        # Check if a patient with this same MRN already exists
        if not patient_api.is_mrn_unique(value):
            raise ValueError("Patient Medical Record Number must be unique")

        mutator = self.mutator("mrn")
        return mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getIdentifiers(self):
        """Returns the identifiers with the field accessor
        """
        accessor = self.accessor("identifiers")
        return accessor(self)

    def get_identifier_items(self):
        """Returns a list of identifier tuples
        """
        identifiers = self.getIdentifiers()
        return list(map(lambda i: (i["key"], i["value"]), identifiers))

    def get_identifier_ids(self):
        """Returns a list of identifier IDs
        """
        identifiers = self.getIdentifiers()
        return list(map(lambda i: i["value"], identifiers))

    @security.protected(permissions.ModifyPortalContent)
    def setIdentifiers(self, value):
        """Set identifiers by the field accessor
        """
        mutator = self.mutator("identifiers")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getRaces(self):
        """Returns the patient races
        """
        accessor = self.accessor("races")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRaces(self, value):
        """Set the patient races
        """
        mutator = self.mutator("races")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEthnicities(self):
        """Returns the patient ethnicities
        """
        accessor = self.accessor("ethnicities")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEthnicities(self, value):
        """Set the patient ethnicities
        """
        mutator = self.mutator("ethnicities")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getMaritalStatus(self):
        """Returns the patient marital status
        """
        accessor = self.accessor("marital_status")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setMaritalStatus(self, value):
        """Set the patient marital status
        """
        mutator = self.mutator("marital_status")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEmailReport(self):
        """Returns the email report option
        """
        accessor = self.accessor("email_report")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEmailReport(self, value):
        """Set the email report option
        """
        mutator = self.mutator("email_report")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getFirstname(self):
        accessor = self.accessor("firstname")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setFirstname(self, value):
        if not isinstance(value, string_types):
            value = u""
        mutator = self.mutator("firstname")
        mutator(self, api.safe_unicode(value.strip()))

    @security.protected(permissions.View)
    def getMiddlename(self):
        accessor = self.accessor("middlename")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMiddlename(self, value):
        if not isinstance(value, string_types):
            value = u""
        mutator = self.mutator("middlename")
        mutator(self, api.safe_unicode(value.strip()))

    @security.protected(permissions.View)
    def getLastname(self):
        accessor = self.accessor("lastname")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setLastname(self, value):
        if not isinstance(value, string_types):
            value = u""
        mutator = self.mutator("lastname")
        mutator(self, api.safe_unicode(value.strip()))

    @security.protected(permissions.View)
    def getFullname(self):
        # Create the fullname from firstname + middlename + lastname
        parts = [self.getFirstname(), self.getMiddlename(), self.getLastname()]
        return " ".join(filter(None, parts))

    ###
    # EMAIL AND PHONE
    ###

    @security.protected(permissions.View)
    def getEmail(self):
        """Get email with the field accessor
        """
        accessor = self.accessor("email")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setEmail(self, value):
        """Set email by the field mutator
        """
        if not isinstance(value, string_types):
            value = u""
        mutator = self.mutator("email")
        mutator(self, api.safe_unicode(value.strip()))

    @security.protected(permissions.View)
    def getAdditionalEmails(self):
        """Returns the email with the field accessor
        """
        accessor = self.accessor("additional_emails")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setAdditionalEmails(self, value):
        """Set email by the field accessor
        """
        mutator = self.mutator("additional_emails")
        mutator(self, value)

    @security.protected(permissions.View)
    def getPhone(self):
        """Get phone by the field accessor
        """
        accessor = self.accessor("phone")
        return accessor(self) or ""

    @security.protected(permissions.ModifyPortalContent)
    def setPhone(self, value):
        """Set phone by the field mutator
        """
        if not isinstance(value, string_types):
            value = u""
        mutator = self.mutator("phone")
        mutator(self, api.safe_unicode(value.strip()))

    @security.protected(permissions.View)
    def getAdditionalPhoneNumbers(self):
        """Get additional phone numbers by the field accessor
        """
        accessor = self.accessor("additional_phone_numbers")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setAdditionalPhoneNumbers(self, value):
        """Set additional phone numbers by the field mutator
        """
        mutator = self.mutator("additional_phone_numbers")
        mutator(self, value)

    @security.protected(permissions.View)
    def getSex(self):
        """Returns the sex with the field accessor
        """
        accessor = self.accessor("sex")
        return accessor(self)

    @security.protected(permissions.View)
    def getSexText(self):
        """Returns the sex with the field accessor
        """
        sexes = dict(SEXES)
        value = self.getSex()
        value = sexes.get(value)
        return translate(value)

    @security.protected(permissions.ModifyPortalContent)
    def setSex(self, value):
        """Set sex by the field accessor
        """
        for k, v in SEXES:
            if value == v:
                value = k
        mutator = self.mutator("sex")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getGender(self):
        """Returns the gender with the field accessor
        """
        accessor = self.accessor("gender")
        return accessor(self)

    @security.protected(permissions.View)
    def getGenderText(self):
        """Returns the gender with the field accessor
        """
        genders = dict(GENDERS)
        value = self.getGender()
        value = genders.get(value)
        return translate(value)

    @security.protected(permissions.ModifyPortalContent)
    def setGender(self, value):
        """Set birthdate by the field accessor
        """
        for k, v in GENDERS:
            if value == v:
                value = k
        mutator = self.mutator("gender")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getBirthdate(self, as_date=True):
        """Returns the birthday with the field accessor
        """
        accessor = self.accessor("birthdate")
        value = accessor(self)
        # Return a plain date object to avoid timezone issues
        # TODO Convert to current timezone and keep it as datetime instead!
        if dtime.is_dt(value) and as_date:
            value = value.date()
        return value

    @security.protected(permissions.View)
    def getLocalizedBirthdate(self):
        """Returns the birthday with the field accessor
        """
        birthdate = dtime.to_DT(self.getBirthdate())
        return dtime.to_localized_time(birthdate)

    @security.protected(permissions.ModifyPortalContent)
    def setBirthdate(self, value):
        """Set birthdate by the field accessor
        """
        mutator = self.mutator("birthdate")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAddress(self):
        """Returns the address with the field accessor
        """
        accessor = self.accessor("address")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAddress(self, value):
        """Set address by the field accessor
        """
        mutator = self.mutator("address")
        return mutator(self, value)

    def getFormattedAddress(self, atype=PHYSICAL_ADDRESS):
        """Returns the formatted address
        """
        if atype not in POSSIBLE_ADDRESSES:
            return None

        address_format = patient_api.get_patient_address_format()

        records = self.getAddress()
        for record in records:
            if atype != record.get("type"):
                continue
            output = Template(address_format).safe_substitute(record)
            output = filter(None, output.split(", "))
            return ", ".join(output)

    @security.protected(permissions.View)
    def getDeceased(self):
        """Returns whether the patient is deceased
        """
        accessor = self.accessor("deceased")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDeceased(self, value):
        """Set if the patient deceased
        """
        mutator = self.mutator("deceased")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getEstimatedBirthdate(self):
        """Returns whether the patient's date of birth is estimated
        """
        accessor = self.accessor("estimated_birthdate")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEstimatedBirthdate(self, value):
        """Set if the patient's date of birth is estimated
        """
        mutator = self.mutator("estimated_birthdate")
        return mutator(self, value)
