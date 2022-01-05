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

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from senaite.app.listing.view import ListingView
from senaite.patient import messageFactory as _sp
from senaite.patient.catalog import PATIENT_CATALOG


class PatientFolderView(ListingView):
    """Global Patient Folder View
    """

    def __init__(self, context, request):
        super(PatientFolderView, self).__init__(context, request)

        self.catalog = PATIENT_CATALOG

        self.contentFilter = {
            "portal_type": "Patient",
            "path": {
                "query": api.get_path(context),
                "level": 0
            },
            "sort_on": "created",
            "sort_order": "descending",
        }

        self.context_actions = {
            _("Add"): {
                "url": "++add++Patient",
                "permission": "Add portal content",
                "icon": "++resource++bika.lims.images/add.png"}
            }

        self.icon = "{}/{}".format(
            self.portal_url, "senaite_theme/icon/patientfolder")

        self.title = _sp("Patients")
        self.description = self.context.Description()
        self.show_select_column = True
        self.pagesize = 25

        self.columns = collections.OrderedDict((
            ("mrn", {
                "title": _("Medical Record #"),
                "index": "patient_mrn"}),
            ("patient_id", {
                "title": _("Patient ID"),
                "index": "patient_id"}),
            ("fullname", {
                "title": _("Fullname"),
                "index": "patient_fullname"}),
            ("email", {
                "title": _("Email"),
                "index": "patient_email"}),
            ("gender", {
                "title": _("Gender"), }),
            ("birthdate", {
                "title": _("Birthdate"), }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def update(self):
        """Update hook
        """
        super(PatientFolderView, self).update()

    def before_render(self):
        """Before template render hook
        """
        super(PatientFolderView, self).before_render()

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        url = api.get_url(obj)

        # MRN
        mrn = obj.get_mrn().encode("utf8")
        item["mrn"] = mrn
        item["replace"]["mrn"] = get_link(
            url, value=mrn)

        # Patient ID
        patient_id = obj.get_patient_id().encode("utf8")
        item["patient_id"] = patient_id
        if patient_id:
            item["replace"]["patient_id"] = get_link(
                url, value=patient_id)

        # Fullname
        fullname = obj.get_fullname().encode("utf8")
        item["fullname"] = fullname
        if fullname:
            item["replace"]["fullname"] = get_link(
                url, value=fullname)

        # Email
        email = obj.get_email()
        item["email"] = email
        if email:
            item["replace"]["email"] = get_email_link(
                email, value=email)

        # Gender
        item["gender"] = obj.get_gender()

        # Birthdate
        birthdate = obj.get_birthdate()
        item["birthdate"] = self.ulocalized_time(birthdate, long_format=0)

        return item
