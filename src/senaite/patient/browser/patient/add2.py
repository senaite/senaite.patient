# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.patient.api import get_patient_name_entry_mode
from bika.lims.browser.analysisrequest.add2 import \
    AnalysisRequestAddView as BaseView


class PatientSampleAddView(BaseView):
    """Patient specific sample add view
    """
    def __init__(self, context, request):
        super(PatientSampleAddView, self).__init__(context, request)

    def get_default_value(self, field, context, arnum):
        """Get the default value of the field
        """
        name = field.getName()
        mrn = self.context.getMRN()

        # Inherit default values from the patient
        if name == "MedicalRecordNumber":
            if not mrn:
                return {"temporary": True, "value": ""}
            return {"temporary": False, "value": mrn}
        elif name == "PatientID":
            return self.context.getPatientID()
        elif name == "PatientFullName":
            entry_mode = get_patient_name_entry_mode()
            if entry_mode == "parts":
                return {
                    "firstname": self.context.getFirstname(),
                    "middlename": self.context.getMiddlename(),
                    "lastname": self.context.getLastname(),
                }
            else:
                return {"firstname": self.context.getFullname()}
        elif name == "PatientAddress":
            address = self.context.getFormattedAddress()
            return api.to_utf8(address)
        elif name == "DateOfBirth":
            birthdate = self.context.getBirthdate()
            if birthdate:
                return birthdate.strftime("%Y-%m-%d")
        elif name == "Sex":
            return self.context.getSex()
        elif name == "Gender":
            return self.context.getGender()

        return super(PatientSampleAddView, self).get_default_value(
            field, context, arnum)
