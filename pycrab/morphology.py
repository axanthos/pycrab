#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File morphology.py

This module provides classes Morphology and Signature, which are used to
describe the morphology of a language in pycrab. The highest-level object is
the Morphology, which has a set of Signature objects as single attribute.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import itertools

from pycrab.null_affix import NULLAffix

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"

NULL_AFFIX = NULLAffix()
"""A module-level constant representing the NULL affix."""


class Morphology(object):
    """A class for implementing an entire morphology in pycrab.

    The Morphology class has only one attribute, namely a list of signatures.
    Stems, suffixes, and prefixes are read-only properties computed on the
    basis of the signatures, and so are suffixal and prefixal parses.

    Examples:
        >>> import pycrab
        >>> morphology = pycrab.Morphology(
        ...     signatures=[
        ...         pycrab.Signature(
        ...             stems=["want", "add", "add"],
        ...             affixes=[pycrab.NULL_AFFIX, "ed", "ing"],
        ...         ),
        ...         pycrab.Signature(
        ...             stems=["cr", "dr"],
        ...             affixes=["y", "ied"],
        ...         ),
        ...         pycrab.Signature(
        ...             stems=["do", "wind"],
        ...             affixes=["un", "re"],
        ...             affix_side="prefix",
        ...         ),
        ...         pycrab.Signature(
        ...             stems=["make", "create"],
        ...             affixes=["re", pycrab.NULL_AFFIX],
        ...             affix_side="prefix",
        ...         ),
        ...     ]
        ... )
        >>> morphology.stems
        {'want', 'dr', 'add', 'do', 'cr', 'wind', 'create', 'make'}
        >>> morphology.suffixes
        {NULL, 'ing', 'ed', 'y', 'ied'}
        >>> morphology.prefixes
        {NULL, 'un', 're'}
        >>> morphology.suffixal_parses
        {('cr', 'ied'), ('want', NULL), ('dr', 'y'), ('cr', 'y'),
        ('add', 'ed'), ('dr', 'ied'), ('want', 'ed'), ('add', NULL),
        ('add', 'ing'), ('want', 'ing')}
        >>> morphology.prefixal_parses
        {(NULL, 'create'), ('re', 'make'), ('un', 'wind'), ('re', 'do'),
        ('re', 'create'), (NULL, 'make'), ('un', 'do'), ('re', 'wind')}

    """

    def __init__(self, signatures=None):
        """__init__ method for class Morphology.

        Args:
            signatures (list, optional): list of signatures in the morphology.
                Defaults to empty list.

        """

        self.signatures = list() if signatures is None else signatures

    def __eq__(self, other_morphology):
        """Tests for morphology equality"""
        if not isinstance(other_morphology, type(self)):
            return False
        if len(other_morphology.signatures) != len(self.signatures):
            return False
        for signature in self.signatures:
            if signature not in other_morphology.signatures:
                return False
        return True

    def __ne__(self, other_morphology):
        """Tests for morphology inequality"""
        return not self == other_morphology

    @property
    def stems(self):
        """Construct a set of stems based on all signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        stems = set()
        for signature in self.signatures:
            stems.update(signature.stems)
        return stems

    @property
    def suffixes(self):
        """Construct a set of suffixes based on all suffixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self._get_affixes()

    @property
    def prefixes(self):
        """Construct a set of prefixes based on all prefixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self._get_affixes(affix_side="prefix")

    def _get_affixes(self, affix_side="suffix"):
        """Construct a set of affixes based on all signatures of a given type.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            set of strings.

        """

        affixes = set()
        for signature in self.signatures:
            if signature.affix_side == affix_side:
                affixes.update(signature.affixes)
        return affixes

    @property
    def suffixal_parses(self):
        """Construct a set of parses based on all suffixal signatures.

        Parses are pairs (stem, suffix).

        Args:
            none.

        Returns:
            set of tuples.

        """

        return self._get_parses()

    @property
    def prefixal_parses(self):
        """Construct a set of parses based on all prefixal signatures.

        Parses are pairs (prefix, stem).

        Args:
            none.

        Returns:
            set of tuples.

        """

        return self._get_parses("prefix")

    def _get_parses(self, affix_side="suffix"):
        """Construct a set of parses based on all signatures of a given type.

        Parses are pairs (prefix, stem) or (stem, suffix), depending on
        affix_side arg.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            set of tuples.

        """

        parses = set()
        for signature in self.signatures:
            if signature.affix_side == affix_side:
                parses.update(signature.parses)
        return parses

    def rebuild_signatures(self, parses, affix_side="suffix"):
        """Reconstruct all signatures of a given type based on a set of parses.

        Args:
            parses (set): pairs (prefix, stem) or (stem, suffix), depending on
                affix_side arg.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            number of signatures constructed (int).

        """

        # List all possible affixes of each stem...
        affixes = collections.defaultdict(list)
        if affix_side == "suffix":
            for stem, suffix in parses:
                affixes[stem].append(suffix)
        else:
            for prefix, stem in parses:
                affixes[stem].append(prefix)

        # Find all stems associated with each affix list...
        stem_lists = collections.defaultdict(set)
        for stem, affixes in affixes.items():
            stem_lists[tuple(sorted(affixes))].add(stem)

        # Rebuild signatures based on list of stems associated with affixes...
        rebuilt_signatures = list()
        for affixes, stems in stem_lists.items():
            rebuilt_signatures.append(
                Signature(stems, affixes, affix_side)
            )

        # Extract existing signatures from other type (not rebuilt)...
        not_rebuilt_signatures = [
            signature for signature in self.signatures
            if signature.affix_side != affix_side
        ]

        # Update list of signatures...
        self.signatures = not_rebuilt_signatures + rebuilt_signatures

        return len(rebuilt_signatures)


class Signature(object):
    """A class for implementing a signature in pycrab.

    The Signature class is at the heart of pycrab's morphology representation
    and learning procedures. A signature has an "affix side" (either "suffix",
    the default, or "prefix"), as well as a dict of stems and a dict of
    affixes, each of which has integer counts as values. Stems and affixes can
    be initialized either with dicts or with other iterables such as lists and
    sets.

    Examples:
        >>> import pycrab
        >>> sig = pycrab.Signature(stems=["add"],
        ...                        affixes={"ing": 8, "ed": 6})
        >>> sig.stems["want"] += 1
        >>> sig.stems["want"] += 1
        >>> sig.stems.update({"play": 2, "guess": 1})
        >>> sig.stems
        {'add': 1, 'want': 2, 'play': 2, 'guess': 1}
        >>> sig.affixes[pycrab.NULL_AFFIX] += 6
        >>> sig.affixes
        {'ing': 8, 'ed': 6, NULL: 6}
        >>> sig2 = pycrab.Signature(stems=["want", "want", "add"])
        >>> sig2.stems
        {'want': 2, 'add': 1}
        >>> sig2.affixes.update({"ing": 1, "ed": 2, pycrab.NULL_AFFIX: 1})
        >>> sig2.robustness
        19
        >>> sig2.parses
        {('add', 'ed'), ('want', NULL), ('want', 'ing'), ('add', 'ing'),
        ('add', NULL), ('want', 'ed')}

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

    def __eq__(self, other_signature):
        """Tests for signature equality"""
        if not isinstance(other_signature, type(self)):
            return False
        if other_signature.affix_side != self.affix_side:
            return False
        if other_signature.stems != self.stems:
            return False
        if other_signature.affixes != self.affixes:
            return False
        return True

    def __ne__(self, other_signature):
        """Tests for signature inequality"""
        return not self == other_signature

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
            set of tuples.

        """

        if self.affix_side == "suffix":
            return set(itertools.product(self.stems, self.affixes))
        return set(itertools.product(self.affixes, self.stems))
