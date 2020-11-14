
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TemporaryMRNViewlet(ViewletBase):
    """ Print a viewlet to display a message stating the Medical Record Number
    assigned to the current Sample is Temporary
    """
    index = ViewPageTemplateFile("templates/temporary_mrn_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(TemporaryMRNViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def is_visible(self):
        """Returns whether this viewlet must be visible or not
        """
        return self.context.isMedicalRecordTemporary()
