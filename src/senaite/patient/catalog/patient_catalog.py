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

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.patient.interfaces import IPatientCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_patient"
CATALOG_TITLE = "Senaite Patient Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("patient_mrn", "", "FieldIndex"),
    ("patient_identifier_keys", "", "KeywordIndex"),
    ("patient_identifier_values", "", "KeywordIndex"),
    ("patient_race_keys", "", "KeywordIndex"),
    ("patient_ethnicity_keys", "", "KeywordIndex"),
    ("patient_marital_status", "", "FieldIndex"),
    ("patient_email", "", "FieldIndex"),
    ("patient_email_report", "", "BooleanIndex"),
    ("patient_fullname", "", "FieldIndex"),
    ("patient_birthdate", "", "DateIndex"),
    ("patient_searchable_text", "", "ZCTextIndex"),
    ("patient_searchable_mrn", "", "ZCTextIndex"),
    ("patient_deceased", "", "BooleanIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "mrn",
]

TYPES = [
    # portal_type name
    "Patient"
]


@implementer(IPatientCatalog)
class PatientCatalog(BaseCatalog):
    """Catalog for Patients
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    @property
    def mapped_catalog_types(self):
        return TYPES


InitializeClass(PatientCatalog)
