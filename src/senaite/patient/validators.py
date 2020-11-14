
from bika.lims import api
from bika.lims.utils import to_utf8
from senaite.patient import messageFactory as _
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implementer


@implementer(IValidator)
class TemporaryIdentifierValidator(object):
    """Verifies the value for a TemporaryIdentifierField is valid
    """
    name = "temporary_identifier_validator"

    def __call__(self, value, *args, **kwargs):
        field = kwargs.get("field", None)
        if not field:
            return True

        identifier = value.get("value", "")
        required = getattr(field, "required", False)
        if required and not identifier:
            field_title = field.widget.label
            msg = _("Required field: ${title}", mapping={"title": field_title})
            ts = api.get_tool("translation_service")
            return to_utf8(ts.translate(msg))

        return True


# Register validators
validation.register(TemporaryIdentifierValidator())
