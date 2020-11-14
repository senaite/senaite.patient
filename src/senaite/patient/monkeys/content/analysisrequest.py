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
# Copyright 2020 by it's authors.
# Some rights reserved, see README and LICENSE.

def isMedicalRecordTemporary(self):  # noqa camelcase, but compliant with AT's
    """Returns whether the Medical Record Number is temporary
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    if mrn.get("temporary"):
        return True
    if not mrn.get("value"):
        return True
    return False


def getMedicalRecordNumberValue(self):  # noqa camelcase, but compliant with AT's
    """Returns the medical record number ID
    """
    mrn = self.getField("MedicalRecordNumber").get(self)
    return mrn.get("value")
