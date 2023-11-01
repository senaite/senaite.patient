# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.adapters.dynamicresultsrange import DynamicResultsRange
from bika.lims.interfaces import IDynamicResultsRange
from dateutil.relativedelta import relativedelta
from senaite.patient import logger
from senaite.patient.api import get_birth_date
from senaite.patient.api import is_ymd
from senaite.patient.api import to_ymd
from zope.interface import implementer

marker = object()


@implementer(IDynamicResultsRange)
class PatientDynamicResultsRange(DynamicResultsRange):
    """Dynamic Results Range Adapter that adds support for additional fields
    that rely on patient information stored at sample level:

    - MinAge: patient's minimum age in ymd format for the range to apply
    - MaxAge: patient's maximum age in ymd format for the range to apply
    - Sex: 'f' (female), 'm' (male)
    """

    def convert(self, value):
        """Converts the given value to a thing that can be compared to values
        entered in the xls file containing the dynamic ranges
        """
        if callable(value):
            value = value()
        if isinstance(value, relativedelta):
            value = to_ymd(value)
        if api.is_uid(value):
            value = api.get_object_by_uid(value)
        if api.is_object(value):
            value = api.get_title(value)
        return value

    def __call__(self):
        """Return the dynamic results range

        The returning dictionary should contain at least the `min` and `max`
        values to override the ResultsRangeDict data.

        :returns: An `IResultsRangeDict` compatible dict
        :rtype: dict
        """
        if self.dynamicspec is None:
            return {}
        # A matching Analysis Keyword is mandatory for any further matches
        keyword = self.analysis.getKeyword()
        by_keyword = self.dynamicspec.get_by_keyword()
        # Get all specs (rows) from the Excel with the same Keyword
        specs = by_keyword.get(keyword)
        if not specs:
            return {}

        # Generate a match data object, which match both the column names and
        # the field names of the Analysis.
        match_data = self.get_match_data()

        # Patient's date of birth
        dob_field = self.analysisrequest.getField("DateOfBirth")
        dob = dob_field.get_date_of_birth(self.analysisrequest)
        sampled = self.analysisrequest.getDateSampled()

        rr = {}

        # Iterate over the rows and return the first where **all** values match
        # with the analysis' values
        for spec in specs:
            skip = False

            for k, v in match_data.items():
                # break if the values do not match
                if v != spec[k]:
                    skip = True
                    break

            # skip the whole specification row
            if skip:
                continue

            # Age/DoB comparison
            min_age = spec.get("MinAge")
            if min_age and is_ymd(min_age):
                if dob and dob > get_birth_date(min_age, on_date=sampled):
                    # patient is younger
                    continue
            elif min_age:
                logger.warn("Not ymd format: {}".format(min_age))

            max_age = spec.get("MaxAge")
            if max_age and is_ymd(max_age):
                if dob and dob < get_birth_date(max_age, on_date=sampled):
                    # patient is older
                    continue
            elif max_age:
                logger.warn("Not ymd format: {}".format(max_age))

            # at this point we have a match, update the results range dict
            for key in self.range_keys:
                value = spec.get(key, marker)
                # skip if the range key is not set in the Excel
                if value is marker:
                    continue
                # skip if the value is not floatable
                if not api.is_floatable(value):
                    continue
                # set the range value
                rr[key] = value
            # return the updated result range
            return rr

        return rr
