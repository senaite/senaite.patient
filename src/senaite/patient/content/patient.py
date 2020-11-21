# -*- coding: utf-8 -*-

from datetime import datetime

from six import string_types

from bika.lims import api
from bika.lims.api.mail import is_valid_email_address
from DateTime import DateTime
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from senaite.patient.config import GENDERS
from senaite.patient.config import PATIENT_CATALOG
from senaite.patient import messageFactory as _
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class IPatient(model.Schema):
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
        description=_(u"Patient ID"),
        required=False,
    )

    name = schema.TextLine(
        title=_(u"label_patient_name", default=u"Name"),
        description=_(u"Patient name"),
        required=False,
    )

    surname = schema.TextLine(
        title=_(u"label_patient_surname", default=u"Surname"),
        description=_(u"Patient surname"),
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

    country = schema.TextLine(
        title=_(u"label_patient_country", default=u"Country"),
        description=_(u"Patient country"),
        required=False,
    )

    directives.widget(
        "birthdate", DatetimeFieldWidget, klass=u"datepicker_nofuture")
    birthdate = schema.Datetime(
        title=_(u"label_patient_birthdate", default=u"Birthdate"),
        description=_(u"Patient birthdate"),
        required=False,
    )

    # Validators

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
        query = {
            "portal_type": "Patient",
            "patient_mrn": data.mrn,
        }
        results = api.search(query, catalog=PATIENT_CATALOG)
        if len(results) > 0:
            for brain in results:
                obj = api.get_object(brain)
                if obj.mrn != data.mrn:
                    continue
                raise Invalid(_("Patient Medical Record # must be unique"))

    @invariant
    def validate_email(data):
        """Checks if the email is correct
        """
        if not data.email:
            return
        if not is_valid_email_address(data.email):
            raise Invalid(_("Patient email is invalid"))


@implementer(IPatient)
class Patient(Item):
    """Results Interpretation Template content
    """

    def Title(self):
        fullname = self.get_fullname()
        return fullname.encode("utf8")

    def get_mrn(self):
        mrn = self.mrn
        if not mrn:
            return u""
        return mrn.strip()

    def get_email(self):
        email = self.email
        if not email:
            return u""
        return email.strip()

    def get_name(self):
        name = self.name
        if not name:
            return u""
        return name.strip()

    def get_surname(self):
        surname = self.surname
        if not surname:
            return u""
        return surname.strip()

    def get_fullname(self):
        name = self.get_name()
        surname = self.get_surname()
        fullname = u"{} {}".format(name, surname).strip()
        if not fullname:
            return self.get_code()
        return fullname

    def get_gender(self):
        genders = dict(GENDERS)
        return genders.get(self.gender)

    def get_birthdate(self):
        if not self.birthdate:
            return None
        return DateTime(self.birthdate)

    def set_birthdate(self, value):
        if isinstance(value, datetime):
            self.birthdate = value
        elif isinstance(value, string_types):
            dt = api.to_date(value)
            value = dt.asdatetime()
        else:
            value = None
        self.birthdate = value

    def set_gender(self, value):
        for k, v in GENDERS:
            if value == v:
                value = k
        self.gender = value
