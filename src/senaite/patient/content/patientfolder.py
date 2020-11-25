# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model

from senaite.core.interfaces import IHideActionsMenu

from zope.interface import implementer


class IPatientFolder(model.Schema):
    """Patient Folder Interface
    """
    pass


@implementer(IPatientFolder, IHideActionsMenu)
class PatientFolder(Container):
    """Patient Folder
    """
    pass
