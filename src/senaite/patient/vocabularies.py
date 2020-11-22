# -*- coding: utf-8 -*-

from senaite.core.locales import COUNTRIES
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


@implementer(IVocabularyFactory)
class CountryVocabulary(object):

    def __call__(self, context):

        items = []
        for country in COUNTRIES:
            value = country.get("Country")
            token = country.get("ISO")
            title = country.get("Country")
            # value, token, title
            term = SimpleTerm(value, token, title)
            items.append(term)
        return SimpleVocabulary(sorted(items, key=lambda t: t.title))


CountryVocabularyFactory = CountryVocabulary()
