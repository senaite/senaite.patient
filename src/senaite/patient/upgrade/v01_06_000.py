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
from zope.annotation.interfaces import IAnnotations

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


def drop_patientfolder_ordering_annotations(tool):
    """Remove the legacy IOrdering annotations from the PatientFolder.

    The PatientFolder now uses `plone.folder.unordered.UnorderedOrdering`
    as its `IOrdering` adapter, so the previous default-ordering
    annotations are no longer maintained:

      - `plone.folder.ordered.order` — a `PersistentList` of every
        child id, mutated on every `_setObject` via
        `DefaultOrdering.notifyAdded`. With one Patient per registered
        sample on a clinical-lab installation, this list grows to many
        tens of thousands of entries; because `PersistentList` has no
        `_p_resolveConflict()`, every concurrent registration that
        creates a new Patient collided on it and the conflict
        propagated all the way to the publisher's retry loop.

      - `plone.folder.ordered.pos` — companion `OIBTree` mapping
        child id -> position. No longer read by anything once the
        adapter is unordered.

    Removing both annotations after the adapter switch frees the
    storage they occupy and removes a stale hot-mutation bucket from
    the ZODB cache. The adapter override is what stops new writes
    from touching them; this step is hygiene.
    """
    logger.info("Dropping IOrdering annotations from PatientFolder ...")
    patients = api.get_portal().patients
    ann = IAnnotations(patients)
    had_order = "plone.folder.ordered.order" in ann
    had_pos = "plone.folder.ordered.pos" in ann
    if not (had_order or had_pos):
        logger.info(
            "Dropping IOrdering annotations from PatientFolder [SKIP] "
            "(no annotations found)")
        return
    ann.pop("plone.folder.ordered.order", None)
    ann.pop("plone.folder.ordered.pos", None)
    patients._p_changed = True
    logger.info("Dropping IOrdering annotations from PatientFolder [DONE]")
