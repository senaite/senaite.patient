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

import transaction
import unittest2 as unittest
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import zope
from plone.testing.z2 import Browser


class SimpleTestLayer(PloneSandboxLayer):
    """Setup Plone with installed AddOn only
    """
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(SimpleTestLayer, self).setUpZope(app, configurationContext)

        import bika.lims
        import senaite.app.listing
        import senaite.app.spotlight
        import senaite.core
        import senaite.impress
        import senaite.lims
        import senaite.patient

        # Load ZCML
        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.lims)
        self.loadZCML(package=senaite.core)
        self.loadZCML(package=senaite.app.listing)
        self.loadZCML(package=senaite.impress)
        self.loadZCML(package=senaite.app.spotlight)
        self.loadZCML(package=senaite.patient)

        # Install product and call its initialize() function
        zope.installProduct(app, "bika.lims")
        zope.installProduct(app, "senaite.lims")
        zope.installProduct(app, "senaite.core")
        zope.installProduct(app, "senaite.app.listing")
        zope.installProduct(app, "senaite.impress")
        zope.installProduct(app, "senaite.app.spotlight")
        zope.installProduct(app, "senaite.patient")

    def setUpPloneSite(self, portal):
        super(SimpleTestLayer, self).setUpPloneSite(portal)
        applyProfile(portal, "senaite.core:default")
        applyProfile(portal, "senaite.patient:default")
        transaction.commit()


###
# Use for simple tests (w/o contents)
###
SIMPLE_FIXTURE = SimpleTestLayer()
SIMPLE_TESTING = FunctionalTesting(
    bases=(SIMPLE_FIXTURE, ),
    name="senaite.patient:SimpleTesting"
)


class SimpleTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])

    def getBrowser(self,
                   username=TEST_USER_NAME,
                   password=TEST_USER_PASSWORD,
                   loggedIn=True):

        # Instantiate and return a testbrowser for convenience
        browser = Browser(self.portal)
        browser.addHeader("Accept-Language", "en-US")
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl("Login Name").value = username
            browser.getControl("Password").value = password
            browser.getControl("Log in").click()
            self.assertTrue("You are now logged in" in browser.contents)
        return browser


class FunctionalTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Member"])
