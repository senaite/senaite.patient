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

from bika.lims.adapters.widgetvisibility import SenaiteATWidgetVisibility
from senaite.patient.api import is_gender_visible


class GenderFieldVisibility(SenaiteATWidgetVisibility):
    """Handles Gender field visibility in Sample add form and view
    """

    def __init__(self, context):
        super(GenderFieldVisibility, self).__init__(
            context=context, sort=10, field_names=["Gender"])

    def isVisible(self, field, mode="view", default="visible"):
        if not is_gender_visible():
            return "invisible"
        return default
