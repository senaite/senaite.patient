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

from bika.lims import api
from bika.lims.utils import get_link
from plone.memoize.instance import memoize
from plone.memoize.view import memoize as viewcache
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.app.listing.utils import add_column
from senaite.app.listing.utils import add_review_state
from senaite.patient import check_installed
from senaite.patient import messageFactory as _
from senaite.patient.api import get_patient_by_mrn
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import implements

# Statuses to add. List of dicts
ADD_STATUSES = [{
    "id": "temp_mrn",
    "title": _("Temporary MRN"),
    "contentFilter": {
        "is_temporary_mrn": True,
        "sort_on": "created",
        "sort_order": "descending",
    },
    "before": "to_be_verified",
    "transitions": [],
    "custom_transitions": [],
},
]

# Columns to add
ADD_COLUMNS = [
    ("Patient", {
        "title": _("Patient"),
        "sortable": False,
        "after": "getId",
    }),
    ("MRN", {
        "title": _("MRN"),
        "sortable": False,
        "index": "medical_record_number",
        "after": "getId",
    }),
]


class SamplesListingAdapter(object):
    """Generic adapter for sample listings
    """
    adapts(IListingView)
    implements(IListingViewAdapter)

    # Priority order of this adapter over others
    priority_order = 99999

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    @property
    @memoize
    def senaite_theme(self):
        return getMultiAdapter(
            (self.context, self.listing.request),
            name="senaite_theme")

    def icon_tag(self, name, **kwargs):
        return self.senaite_theme.icon_tag(name, **kwargs)

    @property
    @memoize
    def show_icon_temp_mrn(self):
        """Returns whether an alert icon has to be displayed next to the sample
        id when the Patient assigned to the sample has a temporary Medical
        Record Number (MRN)
        """
        return api.get_registry_record("senaite.patient.show_icon_temp_mrn")

    @check_installed(None)
    def folder_item(self, obj, item, index):
        if self.show_icon_temp_mrn and obj.isMedicalRecordTemporary:
            # Add an icon after the sample ID
            after_icons = item["after"].get("getId", "")
            kwargs = {"width": 16, "title": _("Temporary MRN")}
            after_icons += self.icon_tag("id-card-red", **kwargs)
            item["after"].update({"getId": after_icons})

        sample_patient_mrn = api.to_utf8(
            obj.getMedicalRecordNumberValue, default="")

        sample_patient_fullname = api.to_utf8(
            obj.getPatientFullName, default="")

        item["MRN"] = sample_patient_mrn
        item["Patient"] = sample_patient_fullname

        # get the patient object
        patient = self.get_patient_by_mrn(sample_patient_mrn)

        if not patient:
            return

        # Link to patient object
        patient_url = api.get_url(patient)
        if sample_patient_mrn:
            item["replace"]["MRN"] = get_link(
                patient_url, sample_patient_mrn)

        patient_mrn = patient.getMRN()
        patient_fullname = patient.getFullname()

        # patient MRN is different
        if sample_patient_mrn != patient_mrn:
            msg = _("Patient MRN of sample is not equal to %s")
            val = api.safe_unicode(patient_mrn) or _("<no value>")
            icon_args = {"width": 16, "title": api.to_utf8(msg % val)}
            item["after"]["MRN"] = self.icon_tag("info", **icon_args)

        if sample_patient_fullname != patient_fullname:
            msg = _("Patient fullname of sample is not equal to %s")
            val = api.safe_unicode(patient_fullname) or _("<no value>")
            icon_args = {"width": 16, "title": api.to_utf8(msg % val)}
            item["after"]["Patient"] = self.icon_tag("info", **icon_args)
        else:
            patient_view_url = "{}/@@view".format(patient_url)
            patient_view_url = get_link(
                    patient_view_url, sample_patient_fullname)
            item["Patient"] = patient_view_url

    @viewcache
    def get_patient_by_mrn(self, mrn):
        if not mrn:
            return None
        if self.is_patient_context():
            return self.context
        return get_patient_by_mrn(mrn)

    @check_installed(None)
    def before_render(self):
        # Additional columns
        rv_keys = map(lambda r: r["id"], self.listing.review_states)
        for column_id, column_values in ADD_COLUMNS:
            # skip MRN column for patient context
            if column_id == "MRN" and self.is_patient_context():
                continue
            add_column(
                listing=self.listing,
                column_id=column_id,
                column_values=column_values,
                after=column_values.get("after", None),
                review_states=rv_keys)

        # Add review_states
        for status in ADD_STATUSES:
            sid = status.get("id")
            # skip temporary MRN for patient context
            if sid == "temp_mrn" and self.is_patient_context():
                continue
            after = status.get("after", None)
            before = status.get("before", None)
            if not status.get("columns"):
                status.update({"columns": self.listing.columns.keys()})
            add_review_state(self.listing, status, after=after, before=before)

    def is_patient_context(self):
        """Check if the current context is a patient
        """
        return api.get_portal_type(self.context) == "Patient"
