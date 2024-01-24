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
Ht                        45  67
Ht                 10y    45  67
Ht          5y     10y    42  66
Ht      m   5y     10y    39  63
------- --- ------ ------ --- ---

The valid ranges for an `Ht` test for a specimen of a 6 years-old male patient
will be `[39;63]`. If no sex has been specificed for the patient or the sex is
femail, the valid range will then be `[42;66]`.

Therefore:

- If the value for column `Sex` is empty (or any of the forms `mf`, `fm`), the
  range will apply for any individual, regardless of sex. Unless another match
  is found that is more specific than the current one.

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

    >>> from DateTime import DateTime
    >>> from six import StringIO
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from openpyxl import Workbook
    >>> from openpyxl.writer.excel import save_virtual_workbook
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.namedfile.file import NamedBlobFile
    >>> import csv

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

    >>> def reset_specification(sample):
    ...     specification = sample.getSpecification()
    ...     sample.setSpecification(None)
    ...     sample.setSpecification(specification)

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
    >>> setup = api.get_setup()

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

Create some baseline objects for the test:

    >>> client = api.create(portal.clients, "Client", Name="Happy Pills", ClientID="HP")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="EDTA", Prefix="EDTA")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Biochemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Biochemistry", Department=department)
    >>> Ht = api.create(setup.bika_analysisservices, "AnalysisService", title="Hematocrit", Keyword="Ht", Category=category)

Create a default specification for the Sample type `EDTA`:

    >>> default_range = {"keyword": "Ht", "min": "35", "max": "60", "warn_min": "34", "warn_max": "61"}
    >>> specification = api.create(setup.bika_analysisspecs, "AnalysisSpec", title="Blood ranges", SampleType=sampletype, ResultsRange=[default_range,])

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
    >>> ds = api.create(setup.dynamic_analysisspecs, "DynamicAnalysisSpec")
    >>> ds.specs_file = to_excel(data)
    >>> specification.setDynamicAnalysisSpec(ds)

Result valid range
..................

Create a new sample:

    >>> sample = new_sample([Ht], specification=specification)
    >>> ht = sample["Ht"]

Since there is no patient assigned, the system returns the generic range:

    >>> get_range(ht)
    ('35', '60')

Make the sample belong to a newborn:

    >>> sample.setDateOfBirth(DateTime())

    >>> # TODO Reset the specification when sample is updated
    >>> reset_specification(sample)

    >>> get_range(sample["Ht"])
    ('45', '67')