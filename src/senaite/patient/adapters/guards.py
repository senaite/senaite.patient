
from bika.lims.interfaces import IGuardAdapter
from zope.interface import implements


class SampleGuardAdapter(object):
    implements(IGuardAdapter)

    def __init__(self, context):
        self.context = context

    def guard(self, action):
        func_name = "guard_{}".format(action)
        func = getattr(self, func_name, None)
        if func:
            return func()

        # No guard intercept here
        return True

    def guard_verify(self):
        """Returns true if the Medical Record Number is not temporary
        """
        return not self.context.isMedicalRecordTemporary()
