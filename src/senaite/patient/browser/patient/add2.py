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
        elif name == "PatientFullName":
            entry_mode = get_patient_name_entry_mode()
            if entry_mode == "parts":
                return {
                    "firstname": self.context.getFirstname(),
                    "middlename": self.context.getMiddlename(),
                    "lastname": self.context.getLastname(),
                }
            elif entry_mode == "first_last":
                return {
                    "firstname": self.context.getFirstname(),
                    "lastname": self.context.getLastname(),
                }
            else:
                return {"firstname": self.context.getFullname()}
        elif name == "PatientAddress":
            address = self.context.getFormattedAddress()
            return api.to_utf8(address)
        elif name == "DateOfBirth":
            from_age = False
            birthdate = self.context.getBirthdate(as_date=False)
            estimated = self.context.getEstimatedBirthdate()
            return [birthdate, from_age, estimated]
        elif name == "Sex":
            return self.context.getSex()
        elif name == "Gender":
            return self.context.getGender()

        return super(PatientSampleAddView, self).get_default_value(
            field, context, arnum)
