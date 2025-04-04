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
from senaite.impress.interfaces import IGroupKeyProvider
from zope.component import adapter
from zope.interface import implementer


@implementer(IGroupKeyProvider)
@adapter(IAnalysisRequest)
class GroupKeyProvider(object):
    """Provide a grouping key for PDF separation
    """
    def __init__(self, context):
        self.context = context

    def __call__(self):
        client_uid = self.context.getClientUID()
        mrn = self.context.getMedicalRecordNumberValue()
        if mrn:
            return "%s_%s" % (client_uid, mrn)
        return client_uid
