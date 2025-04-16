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

from bika.lims import api
from senaite.core.browser.samples.view import SamplesView as BaseView
from senaite.patient import messageFactory as _


class SamplesView(BaseView):
    """Patient Samples View
    """
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        # display "All" samples by default
        self.default_review_state = "all"

        fullname = self.context.getFullname()
        self.title = _(
            "title_patient_samples_listing",
            "Samples of ${patient_fullname}",
            mapping={"patient_fullname": api.safe_unicode(fullname)}
        )

        mrn = self.context.getMRN()
        if mrn:
            self.contentFilter["medical_record_number"] = [mrn]
        else:
            self.contentFilter["medical_record_number"] = []

    def update(self):
        """Called before the listing renders
        """
        super(SamplesView, self).update()
