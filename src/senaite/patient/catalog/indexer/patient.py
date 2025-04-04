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

from plone.indexer import indexer
from senaite.patient.interfaces import IPatient


@indexer(IPatient)
def patient_identifier_keys(instance):
    """Return patient identifier keys
    """
    identifiers = instance.getIdentifiers()
    return map(lambda i: i.get("key"), identifiers)


@indexer(IPatient)
def patient_identifier_values(instance):
    """Return patient identifier values
    """
    identifiers = instance.getIdentifiers()
    return map(lambda i: i.get("value"), identifiers)


@indexer(IPatient)
def patient_race_keys(instance):
    """Return patient race keys
    """
    races = instance.getRaces()
    return map(lambda i: i.get("race"), races)


@indexer(IPatient)
def patient_ethnicity_keys(instance):
    """Return patient ethnicity keys
    """
    ethnicities = instance.getEthnicities()
    return map(lambda i: i.get("ethnicity"), ethnicities)


@indexer(IPatient)
def patient_marital_status(instance):
    """Return patient marital status
    """
    return instance.getMaritalStatus()


@indexer(IPatient)
def patient_mrn(instance):
    """Index Medical Record #
    """
    return instance.getMRN()


@indexer(IPatient)
def patient_fullname(instance):
    """Index fullname
    """
    fullname = instance.getFullname()
    return fullname


@indexer(IPatient)
def patient_email(instance):
    """Index email
    """
    email = instance.getEmail()
    return email


@indexer(IPatient)
def patient_email_report(instance):
    """Index email
    """
    email_report = instance.getEmailReport()
    return email_report


@indexer(IPatient)
def patient_birthdate(instance):
    """Index birthdate
    """
    birthdate = instance.getBirthdate()
    return birthdate


@indexer(IPatient)
def patient_deceased(instance):
    """Index deceased
    """
    return instance.getDeceased()


@indexer(IPatient)
def patient_searchable_text(instance):
    """Index for searchable text queries
    """
    identifier_ids = instance.get_identifier_ids()
    identifier_ids = map(lambda id: id.encode("utf-8"), identifier_ids)
    searchable_text_tokens = [
        instance.getEmail(),
        instance.getMRN(),
        instance.getFullname(),
        instance.getSexText(),
        instance.getGenderText(),
        " ".join(identifier_ids),
    ]
    searchable_text_tokens = filter(None, searchable_text_tokens)
    return " ".join(searchable_text_tokens)


@indexer(IPatient)
def patient_searchable_mrn(instance):
    """Index for searchable Patient MRN queries
    """
    searchable_text_tokens = [
        instance.getMRN(),
        instance.getFirstname(),
        instance.getMiddlename(),
        instance.getLastname(),
    ]
    searchable_text_tokens = filter(None, searchable_text_tokens)
    return " ".join(searchable_text_tokens)
