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

from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from senaite.patient.interfaces import IPatient


@indexer(IAnalysisRequest)
def is_temporary_mrn(instance):
    """Returns whether the Medical Record Number is temporary
    """
    return instance.isMedicalRecordTemporary()


@indexer(IAnalysisRequest)
def medical_record_number(instance):
    """Returns the Medical Record Number value assigned to the sample
    """
    return [instance.getMedicalRecordNumberValue() or None]


@indexer(IPatient)
def patient_mrn(instance):
    """Index Medical Record #
    """
    return instance.get_mrn()


@indexer(IPatient)
def patient_fullname(instance):
    """Index client fullname
    """
    fullname = instance.get_fullname()
    return fullname


@indexer(IPatient)
def patient_email(instance):
    """Index client email
    """
    email = instance.get_email()
    return email


@indexer(IPatient)
def patient_searchable_text(instance):
    """Index for searchable text queries
    """
    searchable_text_tokens = [
        instance.get_email(),
        instance.get_mrn(),
        instance.get_fullname(),
        instance.get_gender(),
    ]
    searchable_text_tokens = filter(None, searchable_text_tokens)
    return u" ".join(searchable_text_tokens)
