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

from senaite.jsonapi import api
from senaite.jsonapi.fieldmanagers import ATFieldManager
from senaite.jsonapi.interfaces import IFieldManager
from zope import interface


class AgeDateOfBirthFieldManager(ATFieldManager):
    """Adapter to get/set the value of AT's AgeDateOfBirthField
    """
    interface.implements(IFieldManager)

    def json_data(self, instance, default=None):
        """Get a JSON compatible value
        """
        dob = self.field.get_date_of_birth(instance)
        from_age = self.field.get_from_age(instance)
        estimated = self.field.get_estimated(instance)

        return [api.to_iso_date(dob), from_age, estimated]
