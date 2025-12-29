Patients Navigation Bar Visibility
===================================

This test ensures that the Patients folder is visible in the navigation bar
after installation, in accordance with the new sidebar navigation system
introduced in senaite.core.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PatientsNavigation


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.registry.interfaces import IRegistry
    >>> from zope.component import getUtility

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> patients = portal.patients

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


Patients Folder Navigation Visibility
--------------------------------------

After installation, the Patients folder should be visible in the navigation bar.
This is configured through three mechanisms:

1. The portal type "PatientFolder" should be in Plone's displayed_types registry:

    >>> registry = getUtility(IRegistry)
    >>> displayed_types = registry.get("plone.displayed_types", ())
    >>> "PatientFolder" in displayed_types
    True

2. The portal type "PatientFolder" should be in SENAITE Setup's sidebar_displayed_types:

    >>> sidebar_displayed_types = setup.getSidebarDisplayedTypes()
    >>> sidebar_displayed_types is not None
    True
    >>> "PatientFolder" in sidebar_displayed_types
    True

3. Since the patients folder is a root folder (direct child of portal), its ID
   should be in SENAITE Setup's sidebar_folders:

    >>> sidebar_folders = setup.getSidebarFolders()
    >>> sidebar_folders is not None
    True
    >>> "patients" in sidebar_folders
    True


Verify Patients Folder Properties
----------------------------------

The patients folder should exist and be properly configured:

    >>> patients is not None
    True

    >>> api.get_portal_type(patients)
    'PatientFolder'

    >>> api.get_id(patients)
    'patients'

    >>> patients.Title()
    'Patients'

The patients folder should be a direct child of the portal:

    >>> api.get_parent(patients) == portal
    True
