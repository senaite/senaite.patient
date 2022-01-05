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

from six import string_types

from bika.lims import api
from bika.lims.api.mail import is_valid_email_address
from DateTime import DateTime
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from senaite.core.schema import DatetimeField
from senaite.core.z3cform.widgets.datetimewidget import DatetimeWidget
from senaite.patient import api as patient_api
from senaite.patient import messageFactory as _
from senaite.patient.catalog import PATIENT_CATALOG
from senaite.patient.config import GENDERS
from senaite.patient.interfaces import IPatient
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


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

    # contact fieldset
    fieldset(
        "contact",
        label=u"Contact",
        fields=["email", "phone", "mobile"])

    # address fieldset
    fieldset(
        "address",
        label=u"Address",
        fields=["city", "zipcode", "address", "country"])

    # Default

    mrn = schema.TextLine(
        title=_(u"label_patient_mrn", default=u"Medical Record #"),
        description=_(u"Patient Medical Record Number"),
        required=True,
    )

    patient_id = schema.TextLine(
        title=_(u"label_patient_id", default=u"ID"),
        description=_(u"Unique Patient ID"),
        required=False,
    )

    firstname = schema.TextLine(
        title=_(u"label_patient_firstname", default=u"Firstname"),
        description=_(u"Patient firstname"),
        required=False,
    )

    lastname = schema.TextLine(
        title=_(u"label_patient_lastname", default=u"Lastname"),
        description=_(u"Patient lastname"),
        required=False,
    )

    gender = schema.Choice(
        title=_(u"label_patient_gender", default=u"Gender"),
        description=_(u"Patient gender"),
        source="senaite.patient.vocabularies.gender",
        default="",
        required=True,
    )

    # Contact

    email = schema.TextLine(
        title=_(u"label_patient_email", default=u"Email"),
        description=_(u"Patient email address"),
        required=False,
    )

    phone = schema.TextLine(
        title=_(u"label_patient_phone", default=u"Phone"),
        description=_(u"Patient phone number"),
        required=False,
    )

    mobile = schema.TextLine(
        title=_(u"label_patient_mobile", default=u"Mobile"),
        description=_(u"Patient mobile phone number"),
        required=False,
    )

    # Address

    address = schema.Text(
        title=_(u"label_patient_address", default=u"Address"),
        description=_(u"Patient address"),
        required=False,
    )

    city = schema.TextLine(
        title=_(u"label_patient_city", default=u"City"),
        description=_(u"Patient city"),
        required=False,
    )

    zipcode = schema.TextLine(
        title=_(u"label_patient_zipcode", default=u"ZIP"),
        description=_(u"Patient ZIP Code"),
        required=False,
    )

    country = schema.Choice(
        title=_(u"label_patient_country", default=u"Country"),
        description=_(u"Patient country"),
        source="senaite.patient.vocabularies.country",
        required=False,
    )

    directives.widget("birthdate",
                      DatetimeWidget,
                      datepicker_nofuture=True,
                      show_time=False)
    birthdate = DatetimeField(
        title=_(u"label_patient_birthdate", default=u"Birthdate"),
        description=_(u"Patient birthdate"),
        required=False,
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

        patient = patient_api.get_patient_by_mrn(
            data.mrn, full_object=False, include_inactive=True)
        if patient:
            raise Invalid(_("Patient Medical Record # must be unique"))

    @invariant
    def validate_patient_id(data):
        """Checks if the patient ID is unique
        """
        pid = data.patient_id

        # field is not required
        if not pid:
            return

        # https://community.plone.org/t/dexterity-unique-field-validation
        context = getattr(data, "__context__", None)
        if context is not None:
            if context.patient_id == pid:
                # nothing changed
                return

        query = {
            "portal_type": "Patient",
            "patient_id": pid,
            "is_active": True,
        }

        patient = patient_api.patient_search(query)

        if patient:
            raise Invalid(_("Patient ID must be unique"))

    @invariant
    def validate_email(data):
        """Checks if the email is correct
        """
        if not data.email:
            return
        if not is_valid_email_address(data.email):
            raise Invalid(_("Patient email is invalid"))


@implementer(IPatient, IPatientSchema)
class Patient(Container):
    """Results Interpretation Template content
    """
    _catalogs = [PATIENT_CATALOG]

    def Title(self):
        fullname = self.get_fullname()
        return fullname.encode("utf8")

    def get_mrn(self):
        return self.mrn

    def set_mrn(self, value):
        value = value.strip()
        if self.mrn == value:
            # noting changed
            return
        if patient_api.get_patient_by_mrn(
                value, full_object=False, include_inactive=True):
            raise ValueError("A patient with that MRN already exists!")
        self.mrn = value

    def get_patient_id(self):
        patient_id = self.patient_id
        if not patient_id:
            return u""
        return self.patient_id

    def set_patient_id(self, value):
        value = value.strip()
        if self.patient_id == value:
            # noting changed
            return
        query = {"portal_type": "Patient", "patient_id": value}
        results = patient_api.patient_search(query)
        if len(results) > 0:
            raise ValueError("A patient with that ID already exists!")
        self.patient_id = value

    def get_firstname(self):
        firstname = self.firstname
        if not firstname:
            return u""
        return firstname.strip()

    def set_firstname(self, value):
        if not isinstance(value, string_types):
            self.firstname = ""
        self.firstname = api.safe_unicode(value)

    def get_lastname(self):
        lastname = self.lastname
        if not lastname:
            return u""
        return lastname.strip()

    def set_lastname(self, value):
        if not isinstance(value, string_types):
            self.lastname = ""
        self.lastname = api.safe_unicode(value)

    def get_fullname(self):
        # Create the fullname from firstname + lastname
        full = filter(None, [self.firstname, self.lastname])
        return " ".join(full).strip()

    def get_email(self):
        email = self.email
        if not email:
            return u""
        return email.strip()

    def get_gender(self):
        genders = dict(GENDERS)
        return genders.get(self.gender)

    def set_gender(self, value):
        for k, v in GENDERS:
            if value == v:
                value = k
        self.gender = value

    def get_birthdate(self):
        if not self.birthdate:
            return None
        return self.birthdate

    def set_birthdate(self, value):
        """Set birthdate field

        Tries to convert value to datetime before set.
        """
        if isinstance(value, DateTime):
            # convert DateTime -> datetime
            value = value.asdatetime()
        elif isinstance(value, string_types):
            # convert string to datetime
            dt = api.to_date(value, None)
            if dt is not None:
                value = dt.asdatetime()
        self.birthdate = value
