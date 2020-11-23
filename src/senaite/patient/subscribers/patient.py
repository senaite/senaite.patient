# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.patient import api as patient_api


def on_before_transition(instance, event):
    """Event handler when a sample was created
    """
    # we only care when reactivating the patient
    if event.new_state != "active":
        return
    mrn = instance.get_mrn()
    patient = patient_api.get_patient_by_mrn(mrn, full_object=False)
    if not patient:
        return True
    # set UID as new MRN #
    uid = api.get_uid(instance)
    instance.set_mrn(api.get_uid(instance))
    # Add warning message
    message = "Duplicate MRN # '{}' was changed to '{}'".format(mrn, uid)
    instance.plone_utils.addPortalMessage(message, "warning")
