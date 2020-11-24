# -*- coding: utf-8 -*-

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
        default=True,
        required=True,
    )


class PatientControlPanelForm(RegistryEditForm):
    schema = IPatientControlPanel
    schema_prefix = "senaite.patient"
    label = _("SENAITE Patient Settings")


PatientControlPanelView = layout.wrap_form(
    PatientControlPanelForm, ControlPanelFormWrapper)
