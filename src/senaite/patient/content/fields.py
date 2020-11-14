import six
from AccessControl import ClassSecurityInfo
from bika.lims.fields import ExtensionField
from Products.Archetypes.Field import ObjectField
from senaite.patient.browser.widgets import TemporaryIdentifierWidget


class TemporaryIdentifierField(ExtensionField, ObjectField):
    """Field Extender of ObjectField that stores a dictionary with two keys:
    {'temporary': bool, 'value': str}, where 'temporary' indicates if the ID has
    to be considered as temporary or not, and 'value' actually represents the ID
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "temporaryidentifier",
        "default": {"temporary": False, "value": ""},
        "widget": TemporaryIdentifierWidget
    })
    security = ClassSecurityInfo()

    def get(self, instance, **kwargs):
        val = super(TemporaryIdentifierField, self).get(instance, **kwargs)
        if isinstance(val, six.string_types):
            val = {"value": val}
        return val
