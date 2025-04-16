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

from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IListingSearchableTextProvider
from plone.indexer import indexer
from senaite.core.interfaces import ISampleCatalog
from senaite.patient.interfaces import ISenaitePatientLayer
from zope.component import adapter
from zope.interface import implementer


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


@adapter(IAnalysisRequest, ISenaitePatientLayer, ISampleCatalog)
@implementer(IListingSearchableTextProvider)
class ListingSearchableTextProvider(object):
    """Adapter that extends existing listing_searchable_text index with
    additional tokens related with patient
    """
    def __init__(self, context, request, catalog):
        self.context = context
        self.request = request
        self.catalog = catalog

    def __call__(self):
        tokens = [
            self.context.getMedicalRecordNumberValue(),
            self.context.getPatientFullName(),
        ]
        return filter(None, tokens)
