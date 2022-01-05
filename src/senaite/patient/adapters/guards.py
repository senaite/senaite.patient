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

from bika.lims import api
from bika.lims.interfaces import IGuardAdapter
from senaite.patient import check_installed
from zope.interface import implements


class SampleGuardAdapter(object):
    implements(IGuardAdapter)

    def __init__(self, context):
        self.context = context

    @check_installed(True)
    def guard(self, action):
        func_name = "guard_{}".format(action)
        func = getattr(self, func_name, None)
        if func:
            return func()

        # No guard intercept here
        return True

    def guard_verify(self):
        """Returns whether the sample can be verified
        """
        temp_mrn = self.context.isMedicalRecordTemporary()
        if temp_mrn:
            # Check whether users can verify samples with a temporary MRN
            if not api.get_registry_record("senaite.patient.verify_temp_mrn"):
                return False

        return True

    def guard_publish(self):
        """Returns whether the sample can be published
        """
        temp_mrn = self.context.isMedicalRecordTemporary()
        if temp_mrn:
            if not api.get_registry_record("senaite.patient.publish_temp_mrn"):
                return False

        return True
