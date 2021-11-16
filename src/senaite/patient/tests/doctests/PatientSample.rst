Patient Workflow
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PatientSample

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from bika.lims.api.security import get_roles_for_permission

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None, **kw):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type)}
    ...     values.update(kw)
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()
    >>> patients = portal.patients
    >>> birthdate = DateTime("1980-02-25")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="General Hospital", ClientID="GH", MemberDiscountApplies=False)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Blood", Prefix="B")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Clinical Lab", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Blood", Department=department)
    >>> MC = api.create(setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)
    >>> MS = api.create(setup.bika_analysisservices, "AnalysisService", title="Malaria Species", Keyword="MS", Price="10", Category=category.UID(), Accredited=True)


Patient Sample Integration
..........................

Create a new sample:

    >>> sample = new_sample([MC, MS], client, contact, sampletype, MedicalRecordNumber={"value": "4711"}, PatientFullName="Clark Kent", Gender="m", DateOfBirth=birthdate)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Check the medical record number:

    >>> sample.getMedicalRecordNumberValue()
    '4711'

Check if the medical record number is temporary:

    >>> sample.isMedicalRecordTemporary()
    False

Get the patient's full name:

    >>> sample.getPatientFullName()
    'Clark Kent'

Get the patient's date of birth:

    >>> sample.getDateOfBirth().strftime("%Y-%m-%d")
    '1980-02-25'

Get the patient's gender:

    >>> sample.getGender()
    'm'

Get the patient's address:

    >>> sample.getPatientAddress()
    ''

Patient reference
.................

When a new patient MRN was referenced in a sample, a new patient is created:

    >>> from senaite.patient.api import get_patient_by_mrn

    >>> patient = get_patient_by_mrn("4711")
    >>> patient
    <Patient at /plone/patients/P000001>

Changing the patient data won't affect the values in a sample:

    >>> patient.get_fullname()
    u'Clark Kent'

    >>> patient.set_firstname("Superman")

    >>> patient.get_fullname()
    u'Superman'

    >>> sample.getPatientFullName()
    'Clark Kent'
