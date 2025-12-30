Patients Navigation Bar Visibility
===================================

This test ensures that the Patients folder is visible in the navigation bar
after installation, in accordance with the new sidebar navigation system
introduced in senaite.core.

Running this test from the buildout directory:

    bin/test -m senaite.patient -t PatientsNavigation


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
This is configured through two mechanisms:

1. The portal type "PatientFolder" should NOT be in SENAITE Setup's sidebar_skip_types
   (types in this list are excluded from the sidebar):

    >>> sidebar_skip_types = setup.getSidebarSkipTypes()
    >>> sidebar_skip_types is not None
    True
    >>> "PatientFolder" not in sidebar_skip_types
    True

2. Since the patients folder is a root folder (direct child of portal), its ID
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
