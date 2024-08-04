Patient Sample
--------------

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
    >>> from senaite.core.api import dtime
    >>> from senaite.patient.api import tuplify_identifiers
    >>> from senaite.patient.api import to_identifier_type_name

Functional Helpers:

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
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()
    >>> patients = portal.patients
    >>> birthdate = DateTime("1980-02-25")
    >>> sampled = DateTime("2023-05-19")

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Test fixture:

    >>> import os
    >>> os.environ["TZ"] = "CET"

We need to create some basic objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="General Hospital", ClientID="GH", MemberDiscountApplies=False)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Blood", Prefix="B")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Clinical Lab", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Blood", Department=department)
    >>> MC = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)
    >>> MS = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Species", Keyword="MS", Price="10", Category=category.UID(), Accredited=True)


Patient Sample Integration
..........................

Create a new sample:

    >>> sample = new_sample(
    ...     [MC, MS], client, contact, sampletype,
    ...     date_sampled=sampled,
    ...     MedicalRecordNumber="4711",
    ...     PatientFullName="Clark Kent",
    ...     Sex="m",
    ...     Gender="d",
    ...     DateOfBirth=birthdate
    ... )
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

Get the patient's date of birth full information:

    >>> sample.getDateOfBirth()
    (datetime.datetime(1980, 2, 25, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>), False, False)

Get the patient's age when sample was collected as timedelta:

    >>> age = sample.getAge()
    >>> [age.years, age.months, age.days]
    [43, 2, 24]

Get the patient's age when the sample was collected in ymd format:

    >>> sample.getAgeYmd()
    '43y 2m 24d'

We can manually set a birth date though, in str/datetime/date format:

    >>> sample.setDateOfBirth("1980-01-25")
    >>> sample.getDateOfBirth()
    (datetime.datetime(1980, 1, 25, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>), False, False)

    >>> sample.setDateOfBirth(DateTime("1980-03-25"))
    >>> sample.getDateOfBirth()
    (datetime.datetime(1980, 3, 25, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>), False, False)

    >>> from datetime import datetime
    >>> sample.setDateOfBirth(datetime(1980, 4, 25))
    >>> sample.getDateOfBirth()
    (datetime.datetime(1980, 4, 25, 0, 0, tzinfo=<DstTzInfo 'CET' CEST+2:00:00 DST>), False, False)

    >>> from datetime import date
    >>> sample.setDateOfBirth(date(1980, 4, 25))
    >>> sample.getDateOfBirth()
    (datetime.datetime(1980, 4, 25, 0, 0, tzinfo=<DstTzInfo 'CET' CEST+2:00:00 DST>), False, False)

And system knows the DoB was directly set as a birth date:

    >>> sample.getDateOfBirthFromAge()
    False

And that is not estimated:

    >>> sample.getDateOfBirthEstimated()
    False

Or we can simply set the Birth date with age in ymd format. In such case, the
system recognizes the date of birth was set from age. Note that sample's
`getAgeYmd` returns the age of the patient when the sample was collected.
Therefore, we need to extract the age directly from the field to properly
assign the age of the patient at present time:

    >>> ymd = sample.getField("DateOfBirth").get_age_ymd(sample)
    >>> sample.setDateOfBirth(ymd)
    >>> dob = sample.getDateOfBirth()
    >>> dtime.to_ansi(dob[0], show_time=False)[:-1]
    '1980042'

And system knows the DoB was calculated from Age:

    >>> sample.getDateOfBirthFromAge()
    True

And also knows it is estimated because of the same reason:

    >>> sample.getDateOfBirthEstimated()
    True

Get the patient's sex:

    >>> sample.getSex()
    'm'

Get the patient's gender:

    >>> sample.getGender()
    'd'

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

    >>> patient.getFullname()
    'Clark Kent'

    >>> patient.setFirstname("Superman")

    >>> patient.getFullname()
    'Superman'

    >>> sample.getPatientFullName()
    'Clark Kent'


Patient Identifiers
...................

Identifiers allow to add multiple IDs for a patient. Each identifier consists
from a type, e.g. *Drivers License* and the actal ID, e.g. *123456789*.

The types of identifiers can be configured in the patient controlpanel, which
stores the values in the registry:

    >>> reg_key = "senaite.patient.identifiers"
    >>> record = api.get_registry_record(reg_key)
    >>> tuplify_identifiers(record)
    [(u'patient_id', u'Patient ID'), (u'passport_id', u'Passport ID'), (u'national_id', u'National ID'), (u'driver_id', u'Driver ID'), (u'voter_id', u'Voter ID')]

Let's add a passport ID for our patient:

    >>> identifiers = [{"key": "passport_id", "value": "123456789"}]
    >>> patient.setIdentifiers(identifiers)
    >>> record = patient.getIdentifiers()
    >>> tuplify_identifiers(record)
    [('passport_id', '123456789')]

Converting the identifier keyword into the title:

    >>> to_identifier_type_name("passport_id")
    u'Passport ID'

    >>> to_identifier_type_name("driver_id")
    u'Driver ID'
