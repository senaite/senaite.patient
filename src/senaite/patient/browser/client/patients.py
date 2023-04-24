# -*- coding: utf-8 -*-

from senaite.patient.browser.patientfolder import PatientFolderView


class PatientsView(PatientFolderView):
    """Client local patients
    """

    def __init__(self, context, request):
        super(PatientsView, self).__init__(context, request)
