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

from senaite.patient import check_installed


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
def getSex(self):  # noqa camelcase
    """Returns the patient's sex
    """
    return self.getField("Sex").get(self)


@check_installed(None)
def setSex(self, value):  # noqa camelcase
    """Sets the patient sex at birth
    """
    return self.getField("Sex").set(self, value)


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
def setDateOfBirth(self, value):  # noqa camelcase
    """Sets the date of birth or age to sample's patient
    """
    self.getField("DateOfBirth").set(self, value)


@check_installed(None)
def getAge(self):  # noqa camelcase
    """Returns the patient's age when the sample was collected
    """
    field = self.getField("DateOfBirth")
    sampled = self.getDateSampled()
    return field.get_age(self, on_date=sampled)


@check_installed(None)
def getAgeYmd(self):  # noqa camelcase
    """Returns the patient's age when the sample was collected in ymd format
    """
    field = self.getField("DateOfBirth")
    sampled = self.getDateSampled()
    return field.get_age_ymd(self, on_date=sampled)


@check_installed(None)
def getDateOfBirthEstimated(self):  # noqa camelcase
    """Returns whether the date of birth is estimated
    """
    field = self.getField("DateOfBirth")
    return field.get_estimated(self)


@check_installed(None)
def getDateOfBirthFromAge(self):  # noqa camelcase
    """Returns whether the date of birth was inferred from age
    """
    field = self.getField("DateOfBirth")
    return field.get_from_age(self)


@check_installed(None)
def getPatientAddress(self):  # noqa camelcase
    """Returns the patient's address
    """
    return self.getField("PatientAddress").get(self)
