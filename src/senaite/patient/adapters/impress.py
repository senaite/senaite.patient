# -*- coding: utf-8 -*-

from bika.lims.interfaces import IAnalysisRequest
from senaite.impress.interfaces import IGroupKeyProvider
from zope.component import adapter
from zope.interface import implementer


@implementer(IGroupKeyProvider)
@adapter(IAnalysisRequest)
class GroupKeyProvider(object):
    """Provide a grouping key for PDF separation
    """
    def __init__(self, context):
        self.context = context

    def __call__(self):
        client_uid = self.context.getClientUID()
        mrn = self.context.getMedicalRecordNumberValue()
        if mrn:
            return "%s_%s" % (client_uid, mrn)
        return client_uid
