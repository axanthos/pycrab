#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File morphology.py

This module provides classes Morphology, Signature, and NULLAffix, which are
used to describe the morphology of a language in pycrab. The highest-level
object is the Morphology, which among other attributes has a list of Signature
objects. A NULLAffix can be part of a list of affixes either in the morphology
itself or in individual signatures.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import itertools

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class Morphology(object):
    """A class for implementing an entire morphology in pycrab.

    The Morphology class serves to store all the elements that compose the
    morphological description of a language in pycrab: signatures, stems,
    suffixes, and prefixes.

    """

    def __init__(self, signatures=None, stems=None, suffixes=None,
                 prefixes=None):
        """__init__ method for class Morphology.

        Args:
            signatures (set, optional): set of signatures in the morphology.
                Defaults to empty set.
            stems (dict, optional): dict of stems in the morphology. The value
                associated with a stem is the signature to which it belongs.
                Defaults to empty dict.
            suffixes (set, optional): set of suffixes in the morphology.
                Defaults to empty set.
            prefixes (set, optional): set of prefixes in the morphology.
                Defaults to empty set.

        """

        self.signatures = set() if signatures is None else set(signatures)
        self.stems = dict() if stems is None else stems
        self.suffixes = set() if suffixes is None else set(suffixes)
        self.prefixes = set() if prefixes is None else set(prefixes)

    @property
    def suffixal_parses(self):
        """Construct a set of parses based on all suffixal signatures.

        Parses are pairs (stem, suffix).

        Args:
            none.

        Returns:
            set.

        """

        return self._get_parses()

    @property
    def prefixal_parses(self):
        """Construct a set of parses based on all prefixal signatures.

        Parses are pairs (prefix, stem).

        Args:
            none.

        Returns:
            set.

        """

        return self._get_parses("prefix")

    def _get_parses(self, affix_side="suffix"):
        """Construct a set of parses based on all signatures of a given type.

        Parses are pairs (prefix, stem) or (stem, suffix), depending on
        affix_side arg.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix"..

        Returns:
            set.

        """

        parses = set()
        for signature in self.signatures:
            if signature.affix_side == affix_side:
                parses.update(parse for parse in signature.parses)
        return parses


class Signature(object):
    """A class for implementing a signature in pycrab.

    The Signature class is at the heart of pycrab's morphology representation
    and learning procedures. A signature has an "affix side" (either "suffix",
    the default, or "prefix"), as well as a dict of stems and a dict of
    affixes, each of which has integer counts as values. Stems and affixes can
    be initialized either with dicts or with other iterables such as lists and
    sets.

    Examples:
        >>> from pycrab import morphology
        >>> sig = morphology.Signature(stems=["add"],
        ...                            affixes={"ing": 8, "ed": 6})
        >>> sig.stems["want"] += 1
        >>> sig.stems["want"] += 1
        >>> sig.stems.update({"play": 2, "guess": 1})
        >>> sig.stems
        {'add': 1, 'want': 2, 'play': 2, 'guess': 1}
        >>> sig.affixes[morphology.NULLAffix()] += 6
        >>> sig.affixes
        {'ing': 8, 'ed': 6, NULL: 6}
        >>> sig2 = morphology.Signature(stems=["want", "want", "add"])
        >>> sig2.stems
        {'want': 2, 'add': 1}
        >>> sig2.affixes.update({"ing": 1, "ed": 2, morphology.NULLAffix(): 1})
        >>> sig2.robustness
        19
        >>> sig2.parses
        {('add', 'ed'), ('want', NULL), ('want', 'ing'), ('add', 'ing'), ('add', NULL), ('want', 'ed')}

    Todo:
        * Compute stability_entropy

    """

    def __init__(self, stems=None, affixes=None, affix_side="suffix"):
        """__init__ method for class Signature.

        Args:
            stems (mapping or iterable, optional): stems associated with this
                signature (with counts if arg is a dict). Defaults to empty
                dict.
            affixes (mapping or iterable, optional): affixes associated with
                this signature (with counts if arg is a dict). Defaults to
                empty dict.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        """
        self.stems = collections.Counter(stems)
        self.affixes = collections.Counter(affixes)
        self.affix_side = affix_side

    @property
    def robustness(self):
        """Returns the robustness of the signature.

        Robustness is the number of letters saved by a signature, which equals
        the sum of the lengths of all words covered by the signature, minus the
        sum of the lengths of stems, minus the sum of the lengths of affixes.

        Returns:
            int.

        """
        saved_stem_length = len("".join(self.stems)) * (len(self.affixes)-1)
        saved_affix_length = len("".join(self.affixes)) * (len(self.stems)-1)
        return saved_stem_length + saved_affix_length

    @property
    def parses(self):
        """Construct a set of parses using the signature's stems and affixes.

        Parses are pairs (prefix, stem) or (stem, suffix).

        Args:
            none.

        Returns:
            set.

        """

        if self.affix_side == "suffix":
            pairs = itertools.product(self.stems, self.affixes)
        else:
            pairs = itertools.product(self.affixes, self.stems)
        return set(pair for pair in pairs)


class NULLAffix(str):
    """A class for representing a NULL affix in pycrab.

    NULL affixes behave like empty strings in most situations, such as when
    being concatenated with stems or when their length is computed, however
    they can be represented by a predefined string ("NULL") when necessary,
    by calling print, str, or repr on them.

    Examples:
        >>> suffix = NULLAffix()
        >>> len(suffix)
        0
        >>> print("test" + suffix)
        test
        >>> print("test", suffix)
        test NULL
        >>> str(suffix)
        'NULL'

    """

    def __init__(self):                 # pylint: disable=super-init-not-called
        """Initializes a NULL affix.

        This method is only here to throw an exception if a NULLAffix is
        initialized with an argument, in order to ensure it is an empty string.

        """

    def __str__(self):
        return "NULL"

    def __repr__(self):
        return self.__str__()
