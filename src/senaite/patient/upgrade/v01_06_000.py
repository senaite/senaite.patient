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

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.patient import logger
from senaite.patient.config import PRODUCT_NAME
from senaite.patient.setuphandlers import display_in_nav

version = "1.6.0"
profile = "profile-{0}:default".format(PRODUCT_NAME)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(PRODUCT_NAME, ver_from,
                                                   version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def fix_clientshareable_behavior(tool):
    """Updates the catalog mappings of senaite registry
    """
    logger.info("Fix IClientShareableBehavior ... ")
    logger.info("Setup Behaviors ...")

    old = "senaite.core.behaviors.IClientShareableBehavior"
    new = "senaite.core.behavior.clientshareable"

    pt = api.get_tool("portal_types")
    fti = pt.get("Patient")
    behaviors = [beh for beh in fti.behaviors if beh != old]
    if new not in behaviors:
        behaviors.append(new)
    fti.behaviors = tuple(behaviors)

    logger.info("Fix IClientShareableBehavior [DONE]")


def display_patients_navbar(tool):
    """Displays the patients's root folder in the navigation bar
    """
    logger.info("Display Patients in navigation bar ...")
    patients = api.get_portal().patients
    display_in_nav(patients)
    logger.info("Display Patients in navigation bar [DONE]")
