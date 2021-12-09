# -*- coding: utf-8 -*-

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
    ("patient_id", "", "FieldIndex"),
    ("patient_mrn", "", "FieldIndex"),
    ("patient_email", "", "FieldIndex"),
    ("patient_fullname", "", "FieldIndex"),
    ("patient_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = BASE_COLUMNS + [
    # attribute name
    "mrn",
    "patient_id",
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
