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

from senaite.patient import check_installed
from senaite.patient.api import get_age_ymd


@check_installed(False)
def isMedicalRecordTemporary(self):  # noqa camelcase, but compliant with AT's
    """Returns whether the Medical Record Number is temporary
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    if not mrn:
        return False
    if mrn.get("temporary"):
        return True
    if not mrn.get("value"):
        return True
    return False


@check_installed(None)
def getMedicalRecordNumberValue(self):  # noqa camelcase, but compliant with AT's
    """Returns the medical record number ID
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    if not mrn:
        return None
    return mrn.get("value")


@check_installed(None)
def getPatientFullName(self):  # noqa camelcase
    """Returns the patient's full name
    """
    return self.getField("PatientFullName").get_fullname(self)


@check_installed(None)
def getPatientID(self):  # noqa camelcase
    """Returns the patient's ID
    """
    return self.getField("PatientID").get(self)


@check_installed(None)
def getGender(self):  # noqa camelcase
    """Returns the patient's gender
    """
    return self.getField("Gender").get(self)


@check_installed(None)
def getDateOfBirth(self):  # noqa camelcase
    """Returns the patient's date of birth
    """
    return self.getField("DateOfBirth").get(self)


@check_installed(None)
def getAge(self):  # noqa camelcase
    """Returns the patient's age when the sample was collected
    """
    dob = getDateOfBirth()
    sampled = self.getDateSampled()
    return get_age_ymd(dob, sampled)


@check_installed(None)
def getPatientAddress(self):  # noqa camelcase
    """Returns the patient's address
    """
    return self.getField("PatientAddress").get(self)
