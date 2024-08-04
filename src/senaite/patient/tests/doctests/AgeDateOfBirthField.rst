AgeDateOfBirthField
-------------------

AgeDateOfBirthField is a field that allows to store the datetime when something
was born, but with support for age and estimated.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t AgeDateOfBirthField

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from datetime import datetime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api import dtime
    >>> from senaite.patient.api import to_ymd

Functional Helpers:

    >>> def new_sample(services, client, contact, sample_type, date_sampled, **kw):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled,
    ...         'SampleType': api.get_uid(sample_type)}
    ...     values.update(kw)
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()
    >>> sampled = DateTime("2020-12-01")
    >>> birth_date = DateTime("1979-12-07")

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
    >>> malaria = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)
    >>> sample = new_sample([malaria], client, contact, sampletype, sampled, DateOfBirth=birth_date)

Get the field:

    >>> field = sample.getField("DateOfBirth")
    >>> field
    <Field DateOfBirth(date_of_birth:rw)>

Get the full information returned by the field for the given sample:

    >>> field.get(sample)
    (datetime.datetime(1979, 12, 7, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>), False, False)

Get the date of birth:

    >>> dob = field.get_date_of_birth(sample)
    >>> dob
    datetime.datetime(1979, 12, 7, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>)

Get the age at current time as timedelta:

    >>> agen = dtime.get_relative_delta(dob, datetime.now())
    >>> age = field.get_age(sample)
    >>> [agen.years, agen.months, agen.days] == [age.years, age.months, age.days]
    True

Get the age at current time in ymd format:

    >>> age_now_ymd = to_ymd(agen)
    >>> age_ymd = field.get_age_ymd(sample)
    >>> age_now_ymd == age_ymd
    True

Get the age at the time when the sample was collected:

    >>> field.get_age(sample, sampled)
    relativedelta(years=+40, months=+11, days=+24)

Get the age at the time when the sample was collected in ymd format:

    >>> field.get_age_ymd(sample, sampled)
    '40y 11m 24d'

Check if the age was set instead of the date of birth:

    >>> field.get_from_age(sample)
    False

Check if the date of birth must be considered as estimated:

    >>> field.get_estimated(sample)
    False

We can set an age instead of a date of birth in ymd format:

    >>> field.set(sample, "43y2m3d")
    >>> field.get_age_ymd(sample)
    '43y 2m 3d'

And the date of birth is calculated automatically:

    >>> dob = field.get_date_of_birth(sample)
    >>> age = field.get_age(sample)
    >>> elapsed = dob + age
    >>> now = datetime.now()
    >>> dtime.to_ansi(elapsed, False) == dtime.to_ansi(now, False)
    True

And since the birth date does has been inferred and we don't have full
information about it (like e.g. hours, minutes, timezone, etc.) both
`estimated` and `from_age` attrs are set to `True`:

    >>> field.get_from_age(sample)
    True

    >>> field.get_estimated(sample)
    True

We can even set the values directly on the setter:

    >>> field.set(sample, birth_date, estimated=True)
    >>> field.get_date_of_birth(sample)
    datetime.datetime(1979, 12, 7, 0, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>)

    >>> field.get_age_ymd(sample, sampled)
    '40y 11m 24d'

    >>> field.get_estimated(sample)
    True

    >>> field.get_from_age(sample)
    False
