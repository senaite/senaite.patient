# -*- coding: utf-8 -*-

from senaite.patient.config import GENDERS
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class GenderVocabulary(object):

    def __call__(self, context):
        items = [
            # value, token, title
            SimpleTerm(value, value, title) for value, title in GENDERS
        ]
        return SimpleVocabulary(items)


GenderVocabularyFactory = GenderVocabulary()
