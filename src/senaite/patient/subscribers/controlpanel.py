# -*- coding: utf-8 -*-

from senaite.patient.api import allow_patients_in_clients


def on_patient_settings_changed(object, event):
    """Event handler when the patient settings changed
    """
    allow = object.allow_patients_in_clients
    allow_patients_in_clients(allow)
