# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PATIENT.
#
# SENAITE.PATIENT is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2020-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.core.api.geo import get_countries
from senaite.patient.config import GENDERS
from senaite.patient.config import NAME_ENTRY_MODES
from senaite.patient.config import SHARE_STRATEGIES
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from bika.lims import api


@implementer(IVocabularyFactory)
class IdentifierVocabulary(object):

    def __call__(self, context):

        identifiers = api.get_registry_record("senaite.patient.identifiers")

        items = []
        for identifier in identifiers:
            # note: the key will get the submitted value
            keyword = identifier.get("key")
            title = identifier.get("value")
            # value, token, title
            term = SimpleTerm(keyword, keyword, title)
            items.append(term)
        return SimpleVocabulary(sorted(items, key=lambda t: t.title))


IdentiierVocabularyFactory = IdentifierVocabulary()


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
        for country in get_countries():
            value = country.name
            token = country.alpha_2
            title = country.name
            # value, token, title
            term = SimpleTerm(value, token, title)
            items.append(term)
        return SimpleVocabulary(sorted(items, key=lambda t: t.title))


CountryVocabularyFactory = CountryVocabulary()


@implementer(IVocabularyFactory)
class NameEntryModesVocabulary(object):

    def __call__(self, context):
        items = [
            # value, token, title
            SimpleTerm(value, value, title) for value, title in NAME_ENTRY_MODES
        ]
        return SimpleVocabulary(items)


NameEntryModesVocabularyFactory = NameEntryModesVocabulary()


@implementer(IVocabularyFactory)
class ShareStrategyVocabulary(object):

    def __call__(self, context):
        items = [
            # value, token, title
            SimpleTerm(value, value, title) for value, title in SHARE_STRATEGIES
        ]
        return SimpleVocabulary(items)


ShareStrategyVocabularyFactory = ShareStrategyVocabulary()
