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
from senaite.patient import api as patient_api


def on_before_transition(instance, event):
    """Event handler when a sample was created
    """
    # we only care when reactivating the patient
    if event.new_state.getId() != "active":
        return
    mrn = instance.get_mrn()
    patient = patient_api.get_patient_by_mrn(mrn, full_object=False)
    if not patient:
        return True
    # set UID as new MRN #
    uid = api.get_uid(instance)
    instance.set_mrn(api.get_uid(instance))
    # Add warning message
    message = "Duplicate MRN # '{}' was changed to '{}'".format(mrn, uid)
    instance.plone_utils.addPortalMessage(message, "warning")
