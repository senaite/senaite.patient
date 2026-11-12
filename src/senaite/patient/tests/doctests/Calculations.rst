Patient data in calculations
----------------------------

A calculation formula reads the results of other analyses and the values of
its interim fields. A formula that depends on the patient, e.g. the estimated
glomerular filtration rate (eGFR), can also read the patient data of the
sample with the functions of `senaite.patient.calc`:

- `age`: the patient's age in whole years on the date sampled
- `sex`: the patient's sex, `m` for male or `f` for female
- `is_female`: `1` if the patient's sex is female, `0` if male
- `is_male`: `1` if the patient's sex is male, `0` if female

The calculation imports them as Additional Python Libraries, and the formula
calls them with the UID of the analysis being calculated, e.g.
`age(%(context_uid)s)`.

When the patient data is missing, the functions raise an error, so the result
is not calculated rather than calculated with a guessed value.

The results not yet verified are recalculated when the sample is modified.

Running this test from the buildout directory:

    bin/test test_doctests -t Calculations


Test Setup
..........

Needed imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.validators import FormulaValidator
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.api.calculation import is_allowed_module
    >>> from senaite.patient import calc
    >>> from zope.lifecycleevent import modified

Functional helpers:

    >>> def new_sample(services, receive=True, **kwargs):
    ...     values = {
    ...         "Client": api.get_uid(client),
    ...         "Contact": api.get_uid(contact),
    ...         "DateSampled": "2026-11-01",
    ...         "SampleType": api.get_uid(sampletype),
    ...     }
    ...     values.update(kwargs)
    ...     uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, uids)
    ...     if receive:
    ...         success, message = do_action_for(sample, "receive")
    ...     return sample

    >>> def get_analysis(sample, keyword):
    ...     analyses = sample.getAnalyses(full_objects=True)
    ...     return [a for a in analyses if a.getKeyword() == keyword][0]

    >>> def set_creatinine(sample, result):
    ...     get_analysis(sample, "CRE").setResult(result)
    ...     get_analysis(sample, "EGFR").calculateResult(override=True)

    >>> def edit(sample, **kwargs):
    ...     api.edit(sample, **kwargs)
    ...     modified(sample)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bika_setup = api.get_bika_setup()
    >>> dob = DateTime("1976-06-15")

Assign default roles for the user to test with:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", ])

Create some baseline objects for the test:

    >>> client = api.create(portal.clients, "Client",
    ...                     Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact",
    ...                      Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType",
    ...                         title="Serum", Prefix="SER")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact",
    ...                         Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department",
    ...                         title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory",
    ...                       title="Biochemistry", Department=department)
    >>> services = bika_setup.bika_analysisservices
    >>> CRE = api.create(services, "AnalysisService",
    ...                  title="Creatinine", Keyword="CRE", Unit="mg/dL",
    ...                  Category=category)

The module is part of the `senaite` package, which calculations must not
import from. senaite.patient registers it as a module for calculations and
adds it to the modules the site allows, so a calculation can import from it:

    >>> is_allowed_module("senaite.patient.calc")
    True

The eGFR with the CKD-EPI 2021 equation, from serum creatinine in mg/dL, age
and sex:

    >>> formula = (
    ...     "142"
    ...     " * min([CRE] / (0.7 if is_female(%(context_uid)s) else 0.9), 1)"
    ...     " ** (-0.241 if is_female(%(context_uid)s) else -0.302)"
    ...     " * max([CRE] / (0.7 if is_female(%(context_uid)s) else 0.9), 1)"
    ...     " ** -1.2"
    ...     " * 0.9938 ** age(%(context_uid)s)"
    ...     " * (1.012 if is_female(%(context_uid)s) else 1)")
    >>> egfr_calc = api.create(setup.calculations, "Calculation",
    ...                        title="eGFR (CKD-EPI 2021)")
    >>> egfr_calc.setPythonImports([
    ...     {"module": "senaite.patient.calc", "function": "age"},
    ...     {"module": "senaite.patient.calc", "function": "is_female"},
    ... ])
    >>> egfr_calc.setFormula(formula)
    >>> EGFR = api.create(services, "AnalysisService",
    ...                   title="eGFR", Keyword="EGFR", Unit="mL/min/1.73m2",
    ...                   Precision=0, Category=category,
    ...                   Calculation=egfr_calc)

And a result that depends on the eGFR:

    >>> low_calc = api.create(setup.calculations, "Calculation",
    ...                       title="Low eGFR")
    >>> low_calc.setFormula("1 if [EGFR] < 60 else 0")
    >>> LOW = api.create(services, "AnalysisService",
    ...                  title="Low eGFR", Keyword="LOW", Category=category,
    ...                  Calculation=low_calc)


The formula
...........

The formula is valid, and it depends on the creatinine only:

    >>> validator = FormulaValidator()
    >>> validator(formula, instance=egfr_calc)
    True

    >>> [api.get_title(s) for s in egfr_calc.getDependentServices()]
    ['Creatinine']


The functions
.............

The functions take the UID of the analysis being calculated:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f")
    >>> uid = api.get_uid(get_analysis(sample, "EGFR"))
    >>> calc.age(uid)
    50
    >>> calc.sex(uid)
    'f'
    >>> calc.is_female(uid)
    1
    >>> calc.is_male(uid)
    0

They refuse a UID other than the one of an analysis of a sample:

    >>> calc.age(api.get_uid(sample))
    Traceback (most recent call last):
    ...
    ValueError: No analysis of a sample with UID '...'

And raise an error when the patient data is missing:

    >>> sample = new_sample([CRE, EGFR])
    >>> uid = api.get_uid(get_analysis(sample, "EGFR"))
    >>> calc.age(uid)
    Traceback (most recent call last):
    ...
    ValueError: No date of birth in sample SER-...
    >>> calc.is_female(uid)
    Traceback (most recent call last):
    ...
    ValueError: No sex in sample SER-...

Or when the date of birth is after the date sampled, rather than returning a
negative age:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f",
    ...                     DateSampled="1976-06-01")
    >>> uid = api.get_uid(get_analysis(sample, "EGFR"))
    >>> calc.age(uid)
    Traceback (most recent call last):
    ...
    ValueError: Date of birth after the date sampled in sample SER-...

A quality control analysis has no patient. Quality control analyses are not
created for results that depend on others, like the eGFR, but the functions
refuse the UID of any of them, e.g. of a creatinine control:

    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Supplier")
    >>> refs = [{"uid": api.get_uid(CRE), "result": "1.0",
    ...          "min": "0.9", "max": "1.1"}]
    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      Blank=False, ReferenceResults=refs,
    ...                      ExpiryDate=DateTime() + 365)
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> qc = worksheet.addReferenceAnalyses(control, [api.get_uid(CRE)])[0]
    >>> calc.age(api.get_uid(qc))
    Traceback (most recent call last):
    ...
    ValueError: No analysis of a sample with UID '...'


Female and male patients
........................

A female patient born on 15 June 1976 is 50 years old on the date sampled.
With a creatinine of 1.0 mg/dL, her eGFR is 69:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> egfr.getResult()
    '68.6...'
    >>> egfr.getFormattedResult()
    '69'

For a male patient of the same age, with the same creatinine, it is 92:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="m")
    >>> set_creatinine(sample, "1.0")
    >>> get_analysis(sample, "EGFR").getFormattedResult()
    '92'


Missing patient data
....................

Without sex, the eGFR is not calculated:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob)
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> egfr.getResult()
    'NA'

Nor without date of birth:

    >>> sample = new_sample([CRE, EGFR], Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> egfr.getResult()
    'NA'

When the patient data is fixed on the sample, the eGFR is recalculated:

    >>> edit(sample, DateOfBirth=dob)
    >>> egfr.getFormattedResult()
    '69'

And when the patient data is removed afterwards, the eGFR is no longer
calculated, also when it is submitted already:

    >>> success, message = do_action_for(get_analysis(sample, "CRE"), "submit")
    >>> success, message = do_action_for(egfr, "submit")
    >>> api.get_review_status(egfr)
    'to_be_verified'

    >>> edit(sample, Sex="")
    >>> egfr.getResult()
    'NA'

    >>> edit(sample, Sex="f")
    >>> egfr.getFormattedResult()
    '69'


Changes before the result is submitted
......................................

A change of the date of birth recalculates the eGFR:

    >>> edit(sample, DateOfBirth=DateTime("1975-06-15"))
    >>> egfr.getResult()
    '68.2...'

So does a change of the date sampled:

    >>> edit(sample, DateSampled=DateTime("2026-06-01"))
    >>> egfr.getResult()
    '68.6...'

And a change of the sex:

    >>> edit(sample, Sex="m")
    >>> egfr.getFormattedResult()
    '92'

The results are recalculated also when the sample is modified by a user who
cannot edit results, e.g. a lab clerk:

    >>> setRoles(portal, TEST_USER_ID, ["LabClerk", ])
    >>> edit(sample, Sex="f")
    >>> egfr.getFormattedResult()
    '69'

    >>> edit(sample, Sex="m")
    >>> egfr.getFormattedResult()
    '92'
    >>> setRoles(portal, TEST_USER_ID, ["LabManager", ])


Changes after the result is submitted
.....................................

A submitted result is recalculated too, until it is verified:

    >>> success, message = do_action_for(get_analysis(sample, "CRE"), "submit")
    >>> success, message = do_action_for(egfr, "submit")
    >>> api.get_review_status(egfr)
    'to_be_verified'

    >>> edit(sample, Sex="f")
    >>> egfr.getFormattedResult()
    '69'

Once verified, the result is kept, e.g. when the sample can still be edited
because other analyses are not verified yet:

    >>> bika_setup.setSelfVerificationEnabled(True)
    >>> sample = new_sample([CRE, EGFR, LOW], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> for keyword in ["CRE", "EGFR"]:
    ...     analysis = get_analysis(sample, keyword)
    ...     success, message = do_action_for(analysis, "submit")
    ...     success, message = do_action_for(analysis, "verify")
    >>> api.get_review_status(egfr)
    'verified'

    >>> edit(sample, Sex="m")
    >>> egfr.getFormattedResult()
    '69'

So is a retracted result, and the retest is recalculated instead:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> success, message = do_action_for(get_analysis(sample, "CRE"), "submit")
    >>> success, message = do_action_for(egfr, "submit")
    >>> success, message = do_action_for(egfr, "retract")
    >>> api.get_review_status(egfr)
    'retracted'
    >>> retest = egfr.getRetest()

    >>> edit(sample, Sex="m")
    >>> egfr.getFormattedResult()
    '69'
    >>> retest.getFormattedResult()
    '92'


Results that are not recalculated
.................................

A rejected result is kept:

    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> success, message = do_action_for(egfr, "reject")
    >>> api.get_review_status(egfr)
    'rejected'

    >>> edit(sample, Sex="m")
    >>> egfr.getFormattedResult()
    '69'

So is the result of a cancelled sample. The sample cannot be edited through
the form anymore, but its fields can still be set by code:

    >>> sample = new_sample([CRE, EGFR], receive=False,
    ...                     DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> success, message = do_action_for(sample, "cancel")
    >>> api.get_review_status(egfr)
    'cancelled'

    >>> sample.getField("Sex").set(sample, "m")
    >>> modified(sample)
    >>> egfr.getFormattedResult()
    '69'

And the results of a disposed sample, which are locked:

    >>> api.get_senaite_setup().setDisposeWorkflowEnabled(True)
    >>> sample = new_sample([CRE, EGFR], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.0")
    >>> egfr = get_analysis(sample, "EGFR")
    >>> success, message = do_action_for(sample, "dispose")
    >>> api.get_review_status(egfr)
    'locked'

    >>> sample.getField("Sex").set(sample, "m")
    >>> modified(sample)
    >>> egfr.getFormattedResult()
    '69'
    >>> api.get_senaite_setup().setDisposeWorkflowEnabled(False)

A result whose calculation does not use the patient data is not recalculated,
e.g. a result entered by hand:

    >>> double_calc = api.create(setup.calculations, "Calculation",
    ...                          title="Double creatinine")
    >>> double_calc.setFormula("[CRE] * 2")
    >>> DOUBLE = api.create(services, "AnalysisService",
    ...                     title="Double creatinine", Keyword="DOUBLE",
    ...                     Category=category, Calculation=double_calc)
    >>> sample = new_sample([CRE, DOUBLE], DateOfBirth=dob, Sex="f")
    >>> get_analysis(sample, "CRE").setResult("1.0")
    >>> double = get_analysis(sample, "DOUBLE")
    >>> double.setResult("5")

    >>> edit(sample, Sex="m")
    >>> double.getResult()
    '5'


Dependent results
.................

The results that depend on a recalculated result are recalculated too:

    >>> sample = new_sample([CRE, EGFR, LOW], DateOfBirth=dob, Sex="f")
    >>> set_creatinine(sample, "1.2")
    >>> low = get_analysis(sample, "LOW")
    >>> low.calculateResult(override=True)
    True
    >>> get_analysis(sample, "EGFR").getFormattedResult()
    '55'
    >>> low.getResult()
    '1'

    >>> edit(sample, Sex="m")
    >>> get_analysis(sample, "EGFR").getFormattedResult()
    '74'
    >>> low.getResult()
    '0'
