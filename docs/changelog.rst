Changelog
=========

1.5.0 (2025-04-04)
------------------

- #123 Hyperlink patient on sample listing
- #119 Rely on `catalog_mappings` to get the catalogs for Patient portal type
- #117 Make accessor and mutator from Patient to rely on base class
- #116 Fix APIError: Expected string type in samples listing
- #115 Fix non-latin names and MRNs comparison in a listing view
- #114 Fix jsonapi returns None for sample's DateOfBirth field
- #113 Added estimated birthdate field to Patient content type
- #112 Use default TZ when calculating birthdate if `on_date` param is not set
- #111 Allow/Disallow the introduction of future dates of birth
- #110 Compatibility with core#2584 (SampleType to DX)
- #108 Fix Traceback when creating partitions when no patient assigned
- #109 Compatibility with core#2563 (Move DynamicAnalysisSpecs to Setup folder)
- #107 Compatibility with core#2567 (AnalysisCategory to DX)
- #106 Skip patient creation if the user has no permissions
- #95  Support for dynamic analysis specs with MinAge, MaxAge and Sex columns
- #98  Allow to flag patients as deceased


1.4.0 (2023-01-10)
------------------

- #104 Display birthdate in the pop-up for patient selection
- #101 Fix sex and gender are not translated properly in patients listing
- #100 Fix AttributeError when DateOfBirth field is hidden in add sample
- #96 Use dtime.to_DT instead of api.to_date
- #99 Do not include default races and ethnicities in locales
- #97 Fix birth date is not displayed in patients listing
- #93 Layered listing searchable text adapter
- #92 Allow searches by patient in samples listing
- #91 Allow only 1 Patient per Report
- #90 Compatibility with core#2399
- #89 Fix addition of snapshots in PatientFolder on Patient creation
- #88 Display all samples by default in Patient context
- #86 Fix non-unique MRNs are permitted when "Require MRN" setting is enabled
- #84 Display "Not defined" in listing for patients without MRN set
- #85 Display MRN instead of fullname in temporary identifier widget
- #83 Fix Patients are not created on Add sample form submit
- #82 Fix traceback when adding a patient
- #79 Fix traceback when creating partitions
- #78 Make to_ymd return a compliant ymd when no elapsed days
- #77 Use system's default timezone for TZ-naive birth dates
- #76 Fix tracbeack on DateOfBirth update while validation fails for others
- #74 Migrate sample's DateOfBirth field to AgeDateOfBirthField
- #72 Move Patient ID to identifiers
- #70 Ensure Require MRN setting is honoured
- #69 Fix Patient Workflows and Permissions
- #68 Allow client local patients
- #66 Fix widget view mode
- #65 Fix cannot create partitions from samples with Patient assigned
- #64 Fix samples without patient middle name
- #63 Fix Traceback in patient's samples view when name has special characters
- #62 Added new name entry mode (firstname + lastname)
- #61 Fix Traceback in listing when fullname is different from sample's
- #60 Fix patient's middlename is not displayed in samples listing
- #59 Migrate Patient MRN/ID Sample Widgets to QuerySelect
- #58 Add sample field validation for patient ID
- #57 Patient samples listing and registration form
- #56 Fix unknown timezone error for birthdate in patient listing
- #54 Allow to set additional named phone numbers
- #55 Optional MRN in Patient Add/Edit forms
- #53 Add patient marital status


1.3.0 (2022-10-03)
------------------

- #51 Add Race and Ethnicity Categories for Patients
- #50 Allow additional email addresses for patients
- #47 Display "Estimated" next to date of birth when estimated from age
- #49 Group configuration settings
- #48 Add Patient middle name
- #46 Added config option to hide age's month and day when older than 1 year
- #45 Added configuration option for Age introduction
- #44 Added Sex as a different field from Gender


1.2.0 (2022-06-13)
------------------

- #42 Remove dependency to Products.TextIndexNG3 (test layer)
- #41 Remove patients action link from inside Patient context
- #40 Add setting to display/hide temporary MRN icon in samples listing
- Fix source distribution package (missing Changelog.rst file)


1.1.0 (2022-06-10)
------------------

- #37 Allow client users to create samples and patients
- #36 Do not display Patient root folder to users other than lab contact
- #35 Integrate new DX address field for patients
- #34 Fix UnicodeDecodeError when storing Patients with special characters
- #31 Allow patient to receive result reports
- #30 Add Patient Identifiers
- #29 Avoid UnknownTimeZoneError when creating patient from Sample
- #28 Remember age/dob selection on context
- #27 Fix cannot create samples with empty Patient ID


1.0.0 (2022-01-05)
------------------

- #25 Add Patient ID in samples
- #24 Migrate patient objects to be folderish
- #23 Integrate new DX date field and widget
- #18 Unique patient ID
- #19 Convert DoB widget to native date input field
- #17 Added marker interface for patients
- #14 Compatibility with Senaite catalog migration
- #8 Added patient workflow and managed permissions
- #7 Added upgrade step handler for senaite.patient
