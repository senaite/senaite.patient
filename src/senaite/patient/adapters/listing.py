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
# Copyright 2020-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.memoize.instance import memoize
from senaite.patient import check_installed
from senaite.patient import messageFactory as _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter
from senaite.app.listing.utils import add_review_state
from senaite.app.listing.utils import add_column
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
    ("MRN", {
        "title": _("MRN"),
        "sortable": False,
        "index": "medical_record_number",
        "after": "getId",
    }),
    ("PatientID", {
        "title": _("Patient ID"),
        "sortable": False,
        "index": "patient_id",
        "after": "MRN",
    }),
    ("Patient", {
        "title": _("Patient"),
        "sortable": False,
        "after": "PatientID",
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

    @check_installed(None)
    def folder_item(self, obj, item, index):
        if obj.isMedicalRecordTemporary:
            # Add an icon after the sample ID
            after_icons = item["after"].get("getId", "")
            kwargs = {"width": 16, "title": _("Temporary MRN")}
            after_icons += self.icon_tag("id-card-red", **kwargs)
            item["after"].update({"getId": after_icons})

        item["MRN"] = obj.getMedicalRecordNumberValue
        item["Patient"] = obj.getPatientFullName
        item["PatientID"] = obj.getPatientID

    @check_installed(None)
    def before_render(self):
        # Additional columns
        rv_keys = map(lambda r: r["id"], self.listing.review_states)
        for column_id, column_values in ADD_COLUMNS:
            add_column(
                listing=self.listing,
                column_id=column_id,
                column_values=column_values,
                after=column_values.get("after", None),
                review_states=rv_keys)

        # Add review_states
        for status in ADD_STATUSES:
            after = status.get("after", None)
            before = status.get("before", None)
            if not status.get("columns"):
                status.update({"columns": self.listing.columns.keys()})
            add_review_state(self.listing, status, after=after, before=before)
