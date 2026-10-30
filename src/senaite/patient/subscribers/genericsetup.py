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

from senaite.patient.api import sync_patients_in_clients

TYPEINFO_STEP = "typeinfo"


def is_typeinfo_imported(event):
    """Returns whether the import ran the type information step
    """
    if event.full_import:
        return True
    return TYPEINFO_STEP in (event.steps or [])


def on_profile_imported(event):
    """Event handler when a profile or an import step was imported

    Restores the patient type in clients after any `typeinfo` import, e.g.
    when an upgrade step of senaite.core imports the type information.
    """
    if not is_typeinfo_imported(event):
        return
    sync_patients_in_clients()
