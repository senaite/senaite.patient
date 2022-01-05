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
from bika.lims.utils import to_utf8
from senaite.patient import messageFactory as _
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implementer


@implementer(IValidator)
class TemporaryIdentifierValidator(object):
    """Verifies the value for a TemporaryIdentifierField is valid
    """
    name = "temporary_identifier_validator"

    def __call__(self, value, *args, **kwargs):
        field = kwargs.get("field", None)
        if not field:
            return True

        identifier = value.get("value", "")
        required = getattr(field, "required", False)
        if required and not identifier:
            field_title = field.widget.label
            msg = _("Required field: ${title}", mapping={"title": field_title})
            ts = api.get_tool("translation_service")
            return to_utf8(ts.translate(msg))

        return True


# Register validators
validation.register(TemporaryIdentifierValidator())
