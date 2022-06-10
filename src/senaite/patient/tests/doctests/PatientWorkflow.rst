Patient Workflow
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PatientWorkflow

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

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type)}
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


Patient Folder Permissions
..........................

Get the mapped workflow and status of the patient folder:

    >>> patients = portal.patients

    >>> api.get_workflows_for(patients)
    ('senaite_patient_folder_workflow',)

    >>> api.get_workflow_status_of(patients)
    'active'

Global add permission:

    >>> from senaite.patient.permissions import AddPatientFolder
    >>> get_roles_for_permission(AddPatientFolder, portal)
    ['Manager']

    >>> from senaite.patient.permissions import AddPatient
    >>> get_roles_for_permission(AddPatient, patients)
    ['LabClerk', 'LabManager', 'Manager']


Patient Permissions
...................

Create a new patient:

    >>> patient = api.create(patients, "Patient", mrn="1", fullname="Clark Kent")
    >>> patient
    <Patient at /plone/patients/P000001>

Workflow and default state:

    >>> api.get_workflows_for(patient)
    ('senaite_patient_workflow',)

    >>> api.get_workflow_status_of(patient)
    'active'

Allowed transitions:

   >>> getAllowedTransitions(patient)
   ['deactivate']

Field permission in **active** state:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

Deactivating the patient

    >>> transitioned = do_action_for(patient, "deactivate")
    >>> api.get_workflow_status_of(patient)
    'inactive'

Field permission in **inactive** state:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, patient)
    []

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, patient)
    []

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, patient)
    []

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, patient)
    []

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, patient)
    []

Reactivate the patient

    >>> transitioned = do_action_for(patient, "activate")
    >>> api.get_workflow_status_of(patient)
    'active'


Patient Sample Permissions
..........................

Create a new sample:

    >>> sample = new_sample([MC, MS], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

All patient fields are editable in `sample_due`:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

All patient fields are editable in `sample_received`:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

Set results and submit:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> ms = filter(lambda an: an.getKeyword() == "MS", analyses)[0]
    >>> mc = filter(lambda an: an.getKeyword() == "MC", analyses)[0]

    >>> ms.setResult(1)
    >>> mc.setResult(100)

    >>> transitioned = do_action_for(ms, "submit")
    >>> transitioned = do_action_for(mc, "submit")

    >>> api.get_workflow_status_of(sample)
    'to_be_verified'

All patient fields are editable in `to_be_verified`:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, sample)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

Verify the results:

    >>> setup.setSelfVerificationEnabled(True)

    >>> transitioned = do_action_for(ms, "verify")
    >>> transitioned = do_action_for(mc, "verify")

    >>> api.get_workflow_status_of(sample)
    'verified'

All patient fields are readonly in `verified`:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, sample)
    []

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, sample)
    []

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, sample)
    []

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, sample)
    []

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, sample)
    []

Publish the sample:

    >>> transitioned = do_action_for(sample, "publish")

    >>> api.get_workflow_status_of(sample)
    'published'

All patient fields are readonly in `published`:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, sample)
    []

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, sample)
    []

    >>> from senaite.patient.permissions import FieldEditGender
    >>> get_roles_for_permission(FieldEditGender, sample)
    []

    >>> from senaite.patient.permissions import FieldEditDateOfBirth
    >>> get_roles_for_permission(FieldEditDateOfBirth, sample)
    []

    >>> from senaite.patient.permissions import FieldEditAddress
    >>> get_roles_for_permission(FieldEditAddress, sample)
    []
