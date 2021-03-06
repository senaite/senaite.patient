# -*- coding: utf-8 -*-

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import get_email_link
from senaite.app.listing.view import ListingView
from senaite.patient import messageFactory as _sp
from senaite.patient.config import PATIENT_CATALOG


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
        birthdate = obj.get_birthdate()
        email = obj.get_email()

        # get_link assumes non-unicode values
        mrn = obj.get_mrn().encode("utf8")
        fullname = obj.get_fullname().encode("utf8")

        item["replace"]["mrn"] = get_link(
            url, value=mrn)
        item["replace"]["fullname"] = get_link(
            url, value=fullname)
        item["replace"]["email"] = get_email_link(
            email, value=email)

        item["gender"] = obj.get_gender()
        item["birthdate"] = self.ulocalized_time(birthdate, long_format=0)

        return item
