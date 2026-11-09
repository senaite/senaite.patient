# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PATIENT.
#
# SENAITE.PATIENT is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2020-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

"""Functions a calculation can use to read the patient data of a sample

A calculation imports them as Additional Python Libraries, with the module
`senaite.patient.calc`, and calls them in its formula with the UID of the
analysis being calculated, e.g.:

    0.9938 ** age(%(context_uid)s)

They raise a `ValueError` when the patient data is missing, so the result is
not calculated rather than calculated with a guessed value.
"""

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis

# The module calculations import the functions from
MODULE = __name__


def get_sample(uid):
    """Returns the sample of the analysis being calculated

    :param uid: UID of the analysis being calculated
    :raises ValueError: when the UID is not the one of an analysis of a sample
    """
    analysis = api.get_object_by_uid(uid, default=None)
    if not IRequestAnalysis.providedBy(analysis):
        raise ValueError("No analysis of a sample with UID '{}'".format(uid))
    return analysis.getRequest()


def age(uid):
    """Returns the patient's age in whole years on the date sampled

    :param uid: UID of the analysis being calculated
    :raises ValueError: when the sample has no date of birth
    """
    sample = get_sample(uid)
    delta = sample.getAge()
    if delta is None:
        raise ValueError("No date of birth in sample {}".format(
            api.get_id(sample)))
    return delta.years


def sex(uid):
    """Returns the patient's sex: `m` for male, `f` for female

    :param uid: UID of the analysis being calculated
    :raises ValueError: when the sex of the sample is not specified
    """
    sample = get_sample(uid)
    value = sample.getSex()
    if value not in ("m", "f"):
        raise ValueError("No sex in sample {}".format(api.get_id(sample)))
    return value


def is_female(uid):
    """Returns 1 if the patient's sex is female, 0 if male

    :param uid: UID of the analysis being calculated
    :raises ValueError: when the sex of the sample is not specified
    """
    return int(sex(uid) == "f")


def is_male(uid):
    """Returns 1 if the patient's sex is male, 0 if female

    :param uid: UID of the analysis being calculated
    :raises ValueError: when the sex of the sample is not specified
    """
    return int(sex(uid) == "m")
