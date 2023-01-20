# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.browser.samples.view import SamplesView as BaseView
from senaite.patient import messageFactory as _


class SamplesView(BaseView):
    """Patient Samples View
    """
    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        fullname = self.context.getFullname()
        self.title = _("Samples of {}").format(api.safe_unicode(fullname))

        mrn = self.context.getMRN()
        if mrn:
            self.contentFilter["medical_record_number"] = [mrn]
        else:
            self.contentFilter["medical_record_number"] = []

    def update(self):
        """Called before the listing renders
        """
        super(SamplesView, self).update()
