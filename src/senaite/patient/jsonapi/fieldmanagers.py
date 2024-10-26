# -*- coding: utf-8 -*-

from senaite.jsonapi import api
from senaite.jsonapi.fieldmanagers import ATFieldManager
from senaite.jsonapi.interfaces import IFieldManager
from zope import interface


class AgeDateOfBirthFieldManager(ATFieldManager):
    """Adapter to get/set the value of AT's AgeDateOfBirthField
    """
    interface.implements(IFieldManager)

    def json_data(self, instance, default=None):
        """Get a JSON compatible value
        """
        dob = self.field.get_date_of_birth(instance)
        from_age = self.field.get_from_age(instance)
        estimated = self.field.get_estimated(instance)

        return [api.to_iso_date(dob), from_age, estimated]
