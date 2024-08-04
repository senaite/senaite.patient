Patient Workflow
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t PatientWorkflow

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from DateTime import DateTime
    >>> from Products.CMFCore.permissions import AccessContentsInformation
    >>> from Products.CMFCore.permissions import AddPortalContent
    >>> from Products.CMFCore.permissions import DeleteObjects
    >>> from Products.CMFCore.permissions import ListFolderContents
    >>> from Products.CMFCore.permissions import ModifyPortalContent
    >>> from Products.CMFCore.permissions import View
    >>> from bika.lims import api
    >>> from bika.lims.api.security import get_roles_for_permission
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

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
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()
    >>> patients = portal.patients

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

We need to create some basic objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="General Hospital", ClientID="GH", MemberDiscountApplies=False)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Blood", Prefix="B")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Clinical Lab", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Blood", Department=department)
    >>> MC = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)
    >>> MS = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Species", Keyword="MS", Price="10", Category=category.UID(), Accredited=True)


Patient Folder Workflow
.......................

Get the mapped workflow and status of the patient folder:

    >>> patients = portal.patients

    >>> api.get_workflows_for(patients)
    ('senaite_patient_folder_workflow',)

    >>> api.get_workflow_status_of(patients)
    'active'


Patient Folder Permissions
..........................

The creation of a patients folder is governed with the custom `AddPatientFolder` permission.
Also see the `initialize` function in `__init__.py`.

    >>> from senaite.patient.permissions import AddPatientFolder
    >>> get_roles_for_permission(AddPatientFolder, portal)
    ['Manager']

The `View` permission governs who is allowed to see the patients folder and if
it is displayed in the side navigation or not:

    >>> get_roles_for_permission(View, patients)
    ['LabClerk', 'LabManager', 'Manager']

The `DeleteObjects` permission governs if it is allowed to delete *any kind of
objects* from this folder:

    >>> get_roles_for_permission(DeleteObjects, patients)
    []

The `AccessContentsInformation` permission governs if the basic access to the
folder, without necessarily viewing it:

    >>> get_roles_for_permission(AccessContentsInformation, patients)
    ['LabClerk', 'LabManager', 'Manager']

The `ListFolderContents` permission governs whether you can get a listing of the patients:

    >>> get_roles_for_permission(ListFolderContents, patients)
    ['LabClerk', 'LabManager', 'Manager']

The `ModifyPortalContent` permission governs whether it is allowed to change e.g. the Title of the folder:

    >>> get_roles_for_permission(ModifyPortalContent, patients)
    ['Manager']


Patient Permissions
...................

The creation of a patients is governed with the custom `AddPatient` permission.
Also see the `initialize` function in `__init__.py`.

    >>> from senaite.patient.permissions import AddPatient
    >>> get_roles_for_permission(AddPatient, patients)
    ['LabClerk', 'LabManager', 'Manager']

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


Default permissions in **active** state:

The following roles can `Access contents information` of patients, e.g. to see
the results in the reference widget:

    >>> get_roles_for_permission(AccessContentsInformation, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']

The `AddPortalContent` permission governs wether it is allowed to add contents
inside a patient.

Although it is not used currently, we use the default permissions including the
`Owner` for client-local patients:

    >>> get_roles_for_permission(AddPortalContent, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

The `DeleteObjects` permission governs wether it is allowed to removed contents
inside a patient. We (almost) never allow this:

    >>> get_roles_for_permission(DeleteObjects, patient)
    []

The `ListFolderContents` permission governs wether it is allowed list contents
inside patients.

Although it is not used currently, we use the default roles including the
`Owner` for client-local and `ClientGuest` for shared patients:

    >>> get_roles_for_permission(ListFolderContents, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']

The `ModifyPortalContent` permission governs wether it is allowed to edit a patient.
Note that we do not allow this for `ClientGuest` role, because we do not want that
shared patients can be edited from basically client contacts:

    >>> get_roles_for_permission(ModifyPortalContent, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

The `View` permission governs if the patient can be viewed:

    >>> get_roles_for_permission(View, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']


Field permission in **active** state:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, patient)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, patient)
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


Default permissions in **inactive** state:

Accessing the patient is possible for the same roles:

    >>> get_roles_for_permission(AccessContentsInformation, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']

It should be no longer possible to add contents to a deactivated patient:

    >>> get_roles_for_permission(AddPortalContent, patient)
    []

Deleting contents is not allowed:

    >>> get_roles_for_permission(DeleteObjects, patient)
    []

Inactive clients should be still listed for the same roles:

    >>> get_roles_for_permission(ListFolderContents, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']

No modifications are allowed for inactive patients:

    >>> get_roles_for_permission(ModifyPortalContent, patient)
    []

Viewing an inactive client is still possible for the same roles

    >>> get_roles_for_permission(View, patient)
    ['ClientGuest', 'LabClerk', 'LabManager', 'Manager', 'Owner']


Field permission in **inactive** state:

    >>> from senaite.patient.permissions import FieldEditMRN
    >>> get_roles_for_permission(FieldEditMRN, patient)
    []

    >>> from senaite.patient.permissions import FieldEditFullName
    >>> get_roles_for_permission(FieldEditFullName, patient)
    []

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, patient)
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

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, sample)
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

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, sample)
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

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, sample)
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

    >>> bika_setup.setSelfVerificationEnabled(True)

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

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, sample)
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

    >>> from senaite.patient.permissions import FieldEditSex
    >>> get_roles_for_permission(FieldEditSex, sample)
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
