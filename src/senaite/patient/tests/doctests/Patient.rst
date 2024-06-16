Patient Object
--------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t Patient


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> patients = portal.patients

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


Patients
--------

All patients are located in the patients folder:

    >>> patient = api.create(patients, "Patient", mrn="1")
    >>> patient
    <Patient at /plone/patients/P000001>

A patient can have a firstname, middlename and lastname:

    >>> api.edit(patient, firstname="Bruce", middlename="Anthony", lastname="Wayne")
    >>> patient.getFullname()
    'Bruce Anthony Wayne'

A patient can have a primary and additional email addresses:

    >>> api.edit(patient, email="bruce@example.com",
    ...          additional_emails=[{"name": "Work", "email": "wayne@example.com"}])

    >>> patient.getEmail()
    'bruce@example.com'

    >>> patient.getAdditionalEmails()
    [{'name': 'Work', 'email': 'wayne@example.com'}]
