Changelog
=========

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
