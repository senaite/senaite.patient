Changelog
=========

1.2.0 (2022-06-13)
------------------

- #43 Allow to share patients with users from different clients groups
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
