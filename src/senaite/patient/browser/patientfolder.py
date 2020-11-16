# -*- coding: utf-8 -*-

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import get_email_link
from senaite.app.listing.view import ListingView
from senaite.patient import messageFactory as _sp


class PatientFolderView(ListingView):
    """Global Patient Folder View
    """

    def __init__(self, context, request):
        super(PatientFolderView, self).__init__(context, request)

        self.catalog = "portal_catalog"

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
            ("code", {
                "title": _("Tax/Fiscal Code"),
                "index": "patient_code"}),
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
            ("client", {
                "title": _("Client"), }),
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
        client = api.get_parent(obj)
        birthdate = obj.get_birthdate()
        email = obj.get_email()

        # get_link assumes non-unicode values
        fullname = obj.get_fullname().encode("utf8")
        client_title = api.get_title(client).encode("utf8")
        code = obj.get_code().encode("utf8")

        item["replace"]["code"] = get_link(
            url, value=code)
        item["replace"]["fullname"] = get_link(
            url, value=fullname)
        item["replace"]["client"] = get_link(
            api.get_url(client), value=client_title)
        item["replace"]["email"] = get_email_link(
            email, value=email)

        item["gender"] = obj.get_gender()
        item["birthdate"] = self.ulocalized_time(birthdate, long_format=0)

        return item
