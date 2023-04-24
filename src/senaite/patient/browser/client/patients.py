# -*- coding: utf-8 -*-

from senaite.patient.browser.patientfolder import PatientFolderView
from senaite.patient.api import is_patient_allowed_in_client


class PatientsView(PatientFolderView):
    """Client local patients
    """

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)

        # remove add action
        if not is_patient_allowed_in_client():
            self.context_actions = {}
