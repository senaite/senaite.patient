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
# Copyright 2020-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api


def translate(msgid, **kwargs):
    """Translate any zope i18n msgid returned from MessageFactory
    """
    msgid = api.safe_unicode(msgid)

    # XX: If the msgid is from type `Message`, Zope's i18n translate tool gives
    #     priority `Message.domain` over the domain passed through kwargs
    domain = kwargs.pop("domain", "senaite.patient")
    params = {
        "domain": getattr(msgid, "domain", domain),
        "context": api.get_request(),
    }
    params.update(kwargs)

    ts = api.get_tool("translation_service")
    return ts.translate(msgid, **params)
