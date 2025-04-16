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

from senaite.core.api import dtime
from senaite.core.browser.form.adapters import EditFormAdapterBase


ESTIMATED_BIRTHDATE_FIELDS = (
    "form.widgets.estimated_birthdate",
    "form.widgets.estimated_birthdate:list"
)
AGE_FIELD = "form.widgets.age"
BIRTHDATE_FIELDS = (
    "form.widgets.birthdate",
    "form.widgets.birthdate-date"
)


class PatientEditForm(EditFormAdapterBase):
    """Edit form for Patient content type
    """

    def initialized(self, data):
        form = data.get("form")
        estimated_birthdate = form.get(ESTIMATED_BIRTHDATE_FIELDS[1])
        self.toggle_and_update_fields(form, estimated_birthdate)
        return self.data

    def modified(self, data):
        if data.get("name") == ESTIMATED_BIRTHDATE_FIELDS[0]:
            estimated_birthdate = data.get("value")
            self.toggle_and_update_fields(
                data.get("form"), estimated_birthdate
            )
        return self.data

    def update_age_field_from_birthdate(self, birthdate):
        age = dtime.get_ymd(birthdate)
        self.add_update_field(AGE_FIELD, age)

    def update_birthdate_field_from_age(self, age):
        birthdate = dtime.get_since_date(age)
        birthdate_str = dtime.date_to_string(birthdate)
        for field in BIRTHDATE_FIELDS:
            self.add_update_field(field, birthdate_str)

    def toggle_and_update_fields(self, form, estimated_birthdate):
        """Toggle age and birthdate fields that depend on estimated_birthdate
        """
        if estimated_birthdate in [True, "selected"]:
            birthdate = form.get(BIRTHDATE_FIELDS[0])
            if birthdate:
                self.update_age_field_from_birthdate(birthdate)
            self.add_show_field(AGE_FIELD)
            self.add_hide_field(BIRTHDATE_FIELDS[0])
        else:
            age = form.get(AGE_FIELD)
            if dtime.is_ymd(age):
                self.update_birthdate_field_from_age(age)
            self.add_show_field(BIRTHDATE_FIELDS[0])
            self.add_hide_field(AGE_FIELD)
