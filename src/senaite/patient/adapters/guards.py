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

from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IGuardAdapter
from zope.interface import implements


class BaseGuardAdapter(object):

    def __init__(self, context):
        self.context = context

    def guard(self, action):
        func_name = "guard_{}".format(action)
        func = getattr(self, func_name, None)
        if func:
            return func()

        # No guard intercept here
        return True


class SampleGuardAdapter(BaseGuardAdapter):
    implements(IGuardAdapter)

    def guard_verify(self):
        """Returns true if the Medical Record Number is not temporary
        """
        return not self.context.isMedicalRecordTemporary()


class PatientGuardAdapter(BaseGuardAdapter):
    implements(IGuardAdapter)

    def guard_deactivate(self):
        """Returns true if patient is not associated to active samples
        """
        mrn = self.context.get_mrn()
        review_states = (
            "sample_registered",
            "scheduled_sampling",
            "to_be_sampled",
            "sample_due",
            "sample_received",
            "attachment_due",
            "to_be_preserved",
            "to_be_verified",
            "verified",
        )
        query = {
            "portal_type": "AnalysisRequest",
            "review_state": review_states,
            "medical_record_number": mrn
        }
        brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        if brains:
            return False
        return True
