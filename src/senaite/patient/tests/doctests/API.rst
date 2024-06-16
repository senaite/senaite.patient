Patient's API
-------------

SENAITE Patient's API provides commonly used functions

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API

Needed Imports:

    >>> from bika.lims.api import create
    >>> from bika.lims.api import do_transition_for
    >>> from bika.lims.api import edit
    >>> from bika.lims.api import get_review_status
    >>> from datetime import date
    >>> from dateutil.relativedelta import relativedelta
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api import dtime
    >>> from senaite.patient import api

Variables:

    >>> portal = self.portal
    >>> request = self.request

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Test fixture:

    >>> import os
    >>> os.environ["TZ"] = "CET"


Convert a period to ymd format
..............................

We can convert a relativedelta to ymd format:

    >>> period = relativedelta(years=1, months=2, days=3)
    >>> api.to_ymd(period)
    '1y 2m 3d'

    >>> period = relativedelta(months=6, days=2)
    >>> api.to_ymd(period)
    '6m 2d'

Or can transform an already existing ymd to its standard format:

    >>> api.to_ymd("1y2m3d")
    '1y 2m 3d'

Zeros and whitespaces are omitted as well:

    >>> api.to_ymd("1y0m   3d")
    '1y 3d'

Returns a TypeError if the value is not of the expected type:

    >>> api.to_ymd(object())
    Traceback (most recent call last):
    [...]
    TypeError: <object object at ... is not supported

Returns a ValueError if the value has the rihgt type, but format is wrong:

    >>> api.to_ymd("")
    Traceback (most recent call last):
    [...]
    ValueError: Not a valid ymd: ''

    >>> api.to_ymd("123")
    Traceback (most recent call last):
    [...]
    ValueError: Not a valid ymd: '123'

    >>> api.to_ymd("y123d")
    Traceback (most recent call last):
    [...]
    ValueError: Not a valid ymd: 'y123d'

And returns a ymd-compliant result when current date or no period is set:

    >>> period = relativedelta()
    >>> api.to_ymd(period)
    '0d'

    >>> api.to_ymd("0y")
    '0d'

    >>> api.to_ymd("0y0m0d")
    '0d'

Function is even aware of monthly and yearly shifts:

    >>> period = relativedelta(years=1235, months=23, days=10)
    >>> api.to_ymd(period)
    '1236y 11m 10d'

    >>> api.to_ymd("1235y23m10d")
    '1236y 11m 10d'

    >>> api.to_ymd("1235y43m10d")
    '1238y 7m 10d'


Check if a value is a ymd
.........................

Returns true for ymd-like strings:

    >>> api.is_ymd("3d")
    True

    >>> api.is_ymd("2m  3d")
    True

    >>> api.is_ymd("0y 2m3d")
    True

    >>> api.is_ymd("0y0m0d")
    True

    >>> api.is_ymd("0d")
    True

But returns false if the format or type is not valid:

    >>> api.is_ymd("y3d")
    False

    >>> api.is_ymd("")
    False

    >>> api.is_ymd(object())
    False

    >>> api.is_ymd(relativedelta())
    False


Get the years, months and days from a period
............................................

We can extract the years, months and days from a period:

    >>> period = relativedelta(years=1, months=2, days=3)
    >>> api.get_years_months_days(period)
    (1, 2, 3)

    >>> period = relativedelta(months=6, days=2)
    >>> api.get_years_months_days(period)
    (0, 6, 2)

    >>> period = relativedelta()
    >>> api.get_years_months_days(period)
    (0, 0, 0)

Periods in ymd format are supported as well:

    >>> api.get_years_months_days("1y2m3d")
    (1, 2, 3)

    >>> api.get_years_months_days("1y0m   3d")
    (1, 0, 3)

Returns a TypeError if the value is not of the expected type:

    >>> api.get_years_months_days(object())
    Traceback (most recent call last):
    [...]
    TypeError: <object object at ... is not supported

Returns a ValueError if the value has the rihgt type, but format is wrong:

    >>> api.get_years_months_days("123")
    Traceback (most recent call last):
    [...]
    ValueError: Not a valid ymd: '123'

    >>> api.get_years_months_days("y123d")
    Traceback (most recent call last):
    [...]
    ValueError: Not a valid ymd: 'y123d'

Function is even aware of monthly and yearly shifts:

    >>> api.get_years_months_days("1235y23m10d")
    (1236, 11, 10)

    >>> api.get_years_months_days("1235y43m10d")
    (1238, 7, 10)


Get the birth date
..................

Having a period, the function returns the date when the event happened relative
to the current date:

    >>> dob = api.get_birth_date("10y1m1d")
    >>> expected = date.today() - relativedelta(years=10, months=1, days=1)
    >>> dtime.to_ansi(dob, False) == dtime.to_ansi(expected, False)
    True

We can also get the birth date having an age and the date when the age was
recorded:

    >>> delta = relativedelta(years=5, months=5)
    >>> on_date = date.today() - delta
    >>> dob = api.get_birth_date("10y1m1d", on_date=on_date)
    >>> expected = on_date - relativedelta(years=10, months=1, days=1)
    >>> dtime.to_ansi(dob, False) == dtime.to_ansi(expected, False)
    True


Get the age
...........

Having a birth date, we can get the age at a given date:

    >>> dob = dtime.to_dt("19791207")
    >>> api.get_age_ymd(dob, on_date="20230518")
    '43y 5m 11d'

If we don't provide an `on_date`, system uses current date:

    >>> ymd = api.get_age_ymd(dob)
    >>> ymd == api.get_age_ymd(dob, on_date=date.today())
    True

Check MRN uniqueness
....................

Patient's API provides an easy function to check if a given MRN exists:

    >>> api.is_mrn_unique("123456")
    True

Create a patient with this very same mrn:

    >>> container = portal.patients
    >>> values = dict(mrn="123456", firstname="John", lastname="Doe", sex="m")
    >>> patient = create(container, "Patient", **values)
    >>> api.is_mrn_unique("123456")
    False

And becomes unique after the mrn of the patient is updated:

    >>> edit(patient, mrn="12345")
    >>> patient.reindexObject()
    >>> api.is_mrn_unique("123456")
    True
    >>> api.is_mrn_unique("12345")
    False

The status of the patient does not have any effect to uniqueness:

    >>> get_review_status(patient)
    'active'
    >>> patient = do_transition_for(patient, "deactivate")
    >>> get_review_status(patient)
    'inactive'
    >>> api.is_mrn_unique("123456")
    True
    >>> api.is_mrn_unique("12345")
    False
