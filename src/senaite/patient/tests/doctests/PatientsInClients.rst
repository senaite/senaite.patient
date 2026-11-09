Patients in Clients
-------------------

The setting "Allow patients in clients" adds the patient type to the
allowed types of clients. Imports of the type information reset these
types, so the setting has to be applied again afterwards.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PatientsInClients

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.registry.interfaces import IRegistry
    >>> from senaite.patient import api as patient_api
    >>> from zope.component import getUtility

Functional Helpers:

    >>> def new_sample(services, client, contact, sample_type, **kw):
    ...     values = {
    ...         "Client": api.get_uid(client),
    ...         "Contact": api.get_uid(contact),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": api.get_uid(sample_type)}
    ...     values.update(kw)
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

    >>> def is_patient_in_client_types():
    ...     fti = api.get_tool("portal_types").getTypeInfo("Client")
    ...     return "Patient" in fti.allowed_content_types

    >>> def remove_patient_from_client_types():
    ...     fti = api.get_tool("portal_types").getTypeInfo("Client")
    ...     types = filter(lambda t: t != "Patient", fti.allowed_content_types)
    ...     fti.allowed_content_types = tuple(types)

    >>> def enable_patients_in_clients(allow=True):
    ...     registry = getUtility(IRegistry)
    ...     registry["senaite.patient.allow_patients_in_clients"] = allow
    ...     patient_api.allow_patients_in_clients(allow)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()
    >>> portal_setup = api.get_tool("portal_setup")

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager",])

We need to create some basic objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="General Hospital", ClientID="GH", MemberDiscountApplies=False)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Blood", Prefix="B")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Clinical Lab", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Blood", Department=department)
    >>> MC = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)


Setting survives an import of the type information
..................................................

Enable patients in clients:

    >>> enable_patients_in_clients()
    >>> is_patient_in_client_types()
    True

Importing the type information of the core profile resets the allowed
types of clients. The patient type is restored afterwards:

    >>> result = portal_setup.runImportStepFromProfile(
    ...     "profile-bika.lims:default", "typeinfo")
    >>> is_patient_in_client_types()
    True

With the setting disabled, the import does not add the patient type:

    >>> enable_patients_in_clients(False)
    >>> result = portal_setup.runImportStepFromProfile(
    ...     "profile-bika.lims:default", "typeinfo")
    >>> is_patient_in_client_types()
    False

    >>> enable_patients_in_clients()

A new patient is created in the client for an unknown MRN:

    >>> sample = new_sample([MC], client, contact, sampletype,
    ...                     MedicalRecordNumber={"value": "MRN-1"})
    >>> patient = patient_api.get_patient_by_mrn("MRN-1")
    >>> api.get_parent(patient) == client
    True


Client type out of sync with the setting
........................................

The upgrade step applies the setting again on existing sites:

    >>> remove_patient_from_client_types()
    >>> is_patient_in_client_types()
    False

    >>> patient_api.sync_patients_in_clients()
    True
    >>> is_patient_in_client_types()
    True

A new site imports the profiles it is set up with before it has a registry,
and every import of the type information notifies the subscriber. Without a
registry nothing is done:

    >>> from plone.registry.interfaces import IRegistry
    >>> from zope.component import getSiteManager
    >>> site_manager = getSiteManager()
    >>> registry = site_manager.getUtility(IRegistry)
    >>> site_manager.unregisterUtility(registry, IRegistry)
    True
    >>> patient_api.sync_patients_in_clients() is None
    True
    >>> site_manager.registerUtility(registry, IRegistry)
    >>> patient_api.sync_patients_in_clients()
    True

If the client type does not accept patients although the setting is
enabled, a sample with an unknown MRN is refused with a clear message:

    >>> remove_patient_from_client_types()
    >>> new_sample([MC], client, contact, sampletype,
    ...            MedicalRecordNumber={"value": "MRN-2"})
    Traceback (most recent call last):
    ...
    ValueError: No patient found with MRN 'MRN-2' and patients cannot be created in '...'. Please check the patient settings.

A sample of a known patient is still created, because no patient has to
be added:

    >>> sample = new_sample([MC], client, contact, sampletype,
    ...                     MedicalRecordNumber={"value": "MRN-1"})
    >>> sample.getMedicalRecordNumberValue()
    'MRN-1'
