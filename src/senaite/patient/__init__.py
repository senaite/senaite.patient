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

import logging

from AccessControl.Permission import addPermission
from AccessControl.SecurityInfo import ModuleSecurityInfo
from bika.lims.api import get_request
from senaite.patient import permissions
from senaite.patient.config import DEFAULT_ROLES
from senaite.patient.config import DEFAULT_TYPES
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.interfaces import ISenaitePatientLayer
from zope.i18nmessageid import MessageFactory

security = ModuleSecurityInfo("senaite.patient")

# Defining a Message Factory for when this product is internationalized.
messageFactory = MessageFactory(PRODUCT_NAME)

logger = logging.getLogger(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not
    """
    request = get_request()
    return ISenaitePatientLayer.providedBy(request)


def check_installed(default_return):
    """Decorator to prevent the function to be called if product not installed
    :param default_return: value to return if not installed
    """
    def is_installed_decorator(func):
        def wrapper(*args, **kwargs):
            if not is_installed():
                return default_return
            return func(*args, **kwargs)
        return wrapper
    return is_installed_decorator


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE PATIENT Customization package ***")

    # Set add permissions
    for typename in DEFAULT_TYPES:
        permid = "Add" + typename
        permname = getattr(permissions, permid)
        security.declarePublic(permid)
        addPermission(permname, default_roles=DEFAULT_ROLES)
