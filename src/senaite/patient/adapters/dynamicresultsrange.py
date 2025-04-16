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

from datetime import datetime

from bika.lims.adapters.dynamicresultsrange import DynamicResultsRange
from bika.lims.interfaces import IDynamicResultsRange
from senaite.core.api import dtime
from senaite.patient.api import get_birth_date
from zope.interface import implementer
from plone.memoize.instance import memoize


@implementer(IDynamicResultsRange)
class PatientDynamicResultsRange(DynamicResultsRange):
    """Dynamic Results Range Adapter that adds support for additional fields
    that rely on patient information stored at sample level:

    - MinAge: patient's minimum age in ymd format for the range to apply
    - MaxAge: patient's maximum age in ymd format for the range to apply
    - Sex: 'f' (female), 'm' (male)
    """

    @property
    @memoize
    def ansi_dob(self):
        """Returns the date of birth of the patient from the current sample
        in ansi format for easy comparison and to avoid TZ issues
        """
        dob_field = self.analysisrequest.getField("DateOfBirth")
        dob = dob_field.get_date_of_birth(self.analysisrequest)
        # convert to ansi to avoid TZ issues
        return dtime.to_ansi(dob)

    def match(self, dynamic_range):
        # Check first for fields that do not require additional logic first
        is_match = super(PatientDynamicResultsRange, self).match(dynamic_range)
        if not is_match:
            return False

        # min and max ages
        min_age = dynamic_range.get("MinAge")
        max_age = dynamic_range.get("MaxAge")

        # patient's date of birth
        if not self.ansi_dob:
            if any([min_age, max_age]):
                # MinAge and/or MaxAge specified, no match
                return False
            return True

        # get the shoulder birth dates when the specimen was collected
        sampled = self.analysisrequest.getDateSampled()
        min_dob = get_birth_date(max_age, sampled, default=datetime.min)
        if self.ansi_dob <= dtime.to_ansi(min_dob):
            # patient is older
            return False

        max_dob = get_birth_date(min_age, sampled, default=datetime.max)
        if self.ansi_dob > dtime.to_ansi(max_dob):
            # patient is younger
            return False

        return True
