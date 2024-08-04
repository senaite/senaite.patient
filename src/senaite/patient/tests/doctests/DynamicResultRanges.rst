Dynamic Result Ranges
---------------------

`senaite.patient` adds support for dynamic ranges with additional columns
`MinAge`, `MaxAge` and `Sex`. Therefore, result values can be evaluated against
ranges that take into account the sex and age of the Patient.

Example
.......

Given is an Excel with the following minimal set of columns:

------- --- ------ ------ --- ---
Keyword Sex MinAge MaxAge min max
------- --- ------ ------ --- ---
Ht                 1d     45  67
Ht          2d     7d     42  66
Ht          8d     14d    39  63
Ht          15d    1m     31  55
Ht          1m     2m     28  42
Ht          3m     6m     29  41
Ht          6m     2y     33  49
Ht          2y     6y     34  40
Ht          6y     12y    35  45
Ht      m   12y    18y    36  51
Ht      f   12y    18y    33  51
Ht      m   18y           39  54
Ht      f   18y           36  48
------- --- ------ ------ --- ---

This Excel is uploaded as a *Dynamic Analysis Specification* object, which is
linked to an Analysis Specification for the Sample Type "EDTA".

A new "EDTA" Sample is created, for which the Hematocrit test (`Ht`) has to
be tested. If the specimen is from a female patient older than 18 years, the
valid range will be `[36;48]`. Likewise, if the specimen is from a patient that
at date of sampling was 3 days old, the valid range will be `[42;66]`.

System searches matches from more specific to less specific. Given the
following list of ranges:

------- --- ------ ------ --- ---
Keyword Sex MinAge MaxAge min max
------- --- ------ ------ --- ---
Ht                        48  70
Ht                 10y    45  67
Ht          5y     10y    42  66
Ht      m   5y     40y    39  63
------- --- ------ ------ --- ---

The valid ranges for an `Ht` test for a specimen of a 6 years-old male patient
will be `[39;63]`. If no sex has been specificed for the patient or the sex is
female, the valid range will then be `[42;66]`.

Therefore:

- If the value for column `Sex` is empty, the range will apply for any
  individual, regardless of sex. Unless another match is found that is more
  specific than the current one.

- If the value for column `MinAge` is empty (or any of the forms `0d`, `0m`,
  `0y` - or combination of them -), the minimum age won't be considered, but
  `MaxAge` only.

- If the value for column `MaxAge` is empty, the maximum age won't be
  considered, but `MinAge` only.

Running this test from the buildout directory:

    bin/test -t DynamicResultRanges.rst

Test Setup
..........

Needed imports:

    >>> import csv
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from openpyxl import Workbook
    >>> from openpyxl.writer.excel import save_virtual_workbook
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.namedfile.file import NamedBlobFile
    >>> from senaite.patient.api import get_birth_date
    >>> from six import StringIO
    >>> from zope.lifecycleevent import modified

Functional Helpers:

    >>> def to_excel(data):
    ...     workbook = Workbook()
    ...     first_sheet = workbook.get_active_sheet()
    ...     reader = csv.reader(StringIO(data))
    ...     for row in reader:
    ...         first_sheet.append(row)
    ...     return NamedBlobFile(save_virtual_workbook(workbook))

    >>> def get_range(analysis):
    ...     rr = ht.getResultsRange()
    ...     return rr["min"], rr["max"]

    >>> def edit(sample, **kwargs):
    ...     api.edit(sample, **kwargs)
    ...     modified(sample)

    >>> def new_sample(services, specification=None):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID(),
    ...         'Analyses': map(api.get_uid, services),
    ...         'Specification': specification or None }
    ...
    ...     sample = create_analysisrequest(client, request, values)
    ...     transitioned = do_action_for(sample, "receive")
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Create some baseline objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="Happy Pills", ClientID="HP")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="EDTA", Prefix="EDTA")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Biochemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Biochemistry", Department=department)
    >>> Ht = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Hematocrit", Keyword="Ht", Category=category)

Create a default specification for the Sample type `EDTA`:

    >>> default_range = {"keyword": "Ht", "min": "35", "max": "60", "warn_min": "34", "warn_max": "61"}
    >>> specification = api.create(bika_setup.bika_analysisspecs, "AnalysisSpec", title="Blood ranges", SampleType=sampletype, ResultsRange=[default_range,])

Assign a DynamicAnalysisSpec with same data as the example given above:

    >>> data = """Keyword,Sex,MinAge,MaxAge,min,max
    ... Ht,,,1d,45,67
    ... Ht,,2d,7d,42,66
    ... Ht,,8d,14d,39,63
    ... Ht,,15d,1m,31,55
    ... Ht,,1m,2m,28,42
    ... Ht,,3m,6m,29,41
    ... Ht,,6m,2y,33,49
    ... Ht,,2y,6y,34,40
    ... Ht,,6y,12y,35,45
    ... Ht,m,12y,18y,36,51
    ... Ht,f,12y,18y,33,51
    ... Ht,m,18y,,39,54
    ... Ht,f,18y,,36,48"""
    >>> ds = api.create(setup.dynamicanalysisspecs, "DynamicAnalysisSpec")
    >>> ds.specs_file = to_excel(data)
    >>> specification.setDynamicAnalysisSpec(ds)

Result valid range
..................

Create a new sample:

    >>> sample = new_sample([Ht], specification=specification)
    >>> sampled = sample.getDateSampled()
    >>> ht = sample["Ht"]

Since there is no patient assigned, the system returns the generic range:

    >>> get_range(ht)
    ('35', '60')

Make the sample belong to a newborn:

    >>> dob = get_birth_date("0d", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('45', '67')

Make the sample belong to a baby (0 to 12 months old):

    >>> dob = get_birth_date("5m", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('29', '41')

Make the sample belong to a toddler (1 to 3 years old). Note min age is
inclusive, while max age is exclusive:

    >>> dob = get_birth_date("2y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('34', '40')

Make the sample belong to a toddler (12 to 18 years old):

    >>> dob = get_birth_date("13y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)

Returns the generic range because sex is not specified:

    >>> get_range(ht)
    ('35', '60')

But returns the valid range if sex is defined:

    >>> edit(sample, Sex="m")
    >>> get_range(ht)
    ('36', '51')

    >>> edit(sample, Sex="f")
    >>> get_range(ht)
    ('33', '51')

Make the sample belong to an adult (> 18 years old):

    >>> dob = get_birth_date("18y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob, Sex="m")
    >>> get_range(ht)
    ('39', '54')

Prioritized ranges
..................

System searches matches from more specific to less specific. Assign a
DynamicAnalysisSpec with same data as the second example given above:

------- --- ------ ------ --- ---
Keyword Sex MinAge MaxAge min max
------- --- ------ ------ --- ---
Ht                        48  70
Ht                 10y    45  67
Ht          5y     10y    42  66
Ht      m   5y     40y    39  63
------- --- ------ ------ --- ---

    >>> data = """Keyword,Sex,MinAge,MaxAge,min,max
    ... Ht,,,,48,70
    ... Ht,,,10y,45,67
    ... Ht,,5y,10y,42,66
    ... Ht,m,5y,40y,39,63"""
    >>> original_data = ds.specs_file
    >>> ds.specs_file = to_excel(data)

Make the sample to be from a female of 2 days, makes the system to return the
range `[45, 67]`, cause is younger than 10y:

    >>> dob = get_birth_date("2d", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob, Sex="f")
    >>> get_range(ht)
    ('45', '67')

If we make the age to be 10y, the system returns the range `[48, 70]`, cause
the `MaxAge` is exclusive and there is no specific range for female:

    >>> dob = get_birth_date("10y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('48', '70')

However, if we make the age to be 7y, the system returns the range `[42, 66]`,
cause the age is within `[5y, 10y)`:

    >>> dob = get_birth_date("7y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('42', '66')

Same with 5y, cause `MinAge` is inclusive:

    >>> dob = get_birth_date("5y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('42', '66')

If we change to male, we have same results as before, except when age is within
`[5y, 10y)` or within `[5y, 40y)`, cause we have an specific entry for male:

    >>> dob = get_birth_date("2d", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob, Sex="m")
    >>> get_range(ht)
    ('45', '67')

    >>> dob = get_birth_date("10y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('39', '63')

    >>> dob = get_birth_date("5y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('39', '63')

    >>> dob = get_birth_date("7y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('39', '63')

And if the age is 40y or above 40y, fallback to `[48, 70]`:

    >>> dob = get_birth_date("40y", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('48', '70')

    >>> dob = get_birth_date("40y1d", on_date=sampled)
    >>> edit(sample, DateOfBirth=dob)
    >>> get_range(ht)
    ('48', '70')

Restore to the initial ranges:

    >>> ds.specs_file = original_data
