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

from builtins import range
import collections
import itertools

import pycrab.utils
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
"""Module-level constant representing the NULL affix."""

MIN_NUM_STEMS = 2
"""Module-level constant for the min number of stems in a signature."""


class Morphology(object):
    """A class for implementing an entire morphology in pycrab.

    The Morphology class has two attributes, namely a list of suffixal
    signatures and a list of prefixal signatures. Stems, suffixes, and prefixes
    are read-only properties computed on the basis of the signatures, and so
    are suffixal and prefixal parses.

    Examples:
        >>> import pycrab
        >>> morphology = pycrab.Morphology(
        ...     suffixal_signatures=[
        ...         pycrab.Signature(
        ...             stems=["want", "add", "add"],
        ...             affixes=[pycrab.NULL_AFFIX, "ed", "ing"],
        ...         ),
        ...         pycrab.Signature(
        ...             stems=["cr", "dr"],
        ...             affixes=["y", "ied"],
        ...         ),
        ...     ],
        ...     prefixal_signatures=[
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
        ...     ],
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

    Todo:
        - add min_stem_length constraint? in build_signatures?

    """

    def __init__(self, suffixal_signatures=None, prefixal_signatures=None):
        """__init__ method for class Morphology.

        Args:
            suffixal_signatures (list, optional): list of suffixal signatures
                in the morphology. Defaults to empty list.
            prefixal_signatures (list, optional): list of prefixal signatures
                in the morphology. Defaults to empty list.

        """

        if suffixal_signatures is None:
            self.suffixal_signatures = list()
        else:
            self.suffixal_signatures = suffixal_signatures
        if prefixal_signatures is None:
            self.prefixal_signatures = list()
        else:
            self.prefixal_signatures = prefixal_signatures

    def __eq__(self, other_morphology):
        """Tests for morphology equality."""
        if not isinstance(other_morphology, type(self)):
            return False
        if (len(other_morphology.suffixal_signatures)
                != len(self.suffixal_signatures)):
            return False
        if (len(other_morphology.prefixal_signatures)
                != len(self.prefixal_signatures)):
            return False
        for signature in self.suffixal_signatures:
            if signature not in other_morphology.suffixal_signatures:
                return False
        for signature in self.prefixal_signatures:
            if signature not in other_morphology.prefixal_signatures:
                return False
        return True

    def __ne__(self, other_morphology):
        """Tests for morphology inequality."""
        return not self == other_morphology

    def __str__(self):
        """Formats the morphology for display."""

        lines = list()

        # Suffixal signatures
        for signature in sorted(self.suffixal_signatures,
                                key=lambda signature: signature.robustness,
                                reverse=True):
            lines.append(str(signature))

        # Prefixal signatures
        # TODO: is it ok to simply print suffixal then prefixal sigs? Or do
        # we rather want to have them all sorted by robustness? In the former
        # case do we add some kind of title before each type? In the latter 
        # case do we add some kind of indication of the type of each signature?
        for signature in sorted(self.prefixal_signatures,
                                key=lambda signature: signature.robustness,
                                reverse=True):
            lines.append(str(signature))

        return "\n".join(lines)

    @property
    def stems(self):
        """Construct a set of stems based on all signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        stems = set()
        for signature in self.suffixal_signatures + self.prefixal_signatures:
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
        if affix_side == "suffix":
            signatures = self.suffixal_signatures
        else:
            signatures = self.prefixal_signatures
        for signature in signatures:
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

        return self._get_parses(affix_side="prefix")

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
        if affix_side == "suffix":
            signatures = self.suffixal_signatures
        else:
            signatures = self.prefixal_signatures
        for signature in signatures:
            parses.update(signature.parses)
        return parses

    def build_signatures(self, parses, affix_side="suffix",
                         min_num_stems=MIN_NUM_STEMS):
        """Construct all signatures of a given type based on a set of parses.

        Args:
            parses (set): pairs (prefix, stem) or (stem, suffix), depending on
                affix_side arg.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).

        Returns:
            number of signatures constructed (int).

        """

        # List all possible affixes of each stem...
        affixes = collections.defaultdict(list) # TODO: set instead of list?
        if affix_side == "suffix":
            for stem, suffix in parses:
                affixes[stem].append(suffix)
        else:
            for prefix, stem in parses:
                affixes[stem].append(prefix)

        # Find all stems associated with each affix list...
        stem_sets = collections.defaultdict(set)
        for stem, affixes in affixes.items():
            stem_sets[tuple(sorted(affixes))].add(stem)

        # Build signatures based on sets of stems associated with affixes...
        signatures = list()
        for affixes, stems in stem_sets.items():
            if len(stems) >= min_num_stems:     # Require min number of stems.
                signatures.append(Signature(stems, affixes, affix_side))

        # Update list of signatures of required type...
        if affix_side == "suffix":
            self.suffixal_signatures = signatures
        else:
            self.prefixal_signatures = signatures

        return len(signatures)

    def _add_test_signatures(self):
        """"Add signatures to morphology for testing purposes."""
        self.suffixal_signatures.append(
            pycrab.Signature(
                stems=["want", "add", "add"],
                affixes=[pycrab.NULL_AFFIX, "ed", "ing"],
            )
        )
        self.suffixal_signatures.append(
            pycrab.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            )
        )
        self.prefixal_signatures.append(
            pycrab.Signature(
                stems=["do", "wind"],
                affixes=["un", "re"],
                affix_side="prefix",
            )
        )
        self.prefixal_signatures.append(
            pycrab.Signature(
                stems=["make", "create"],
                affixes=["re", pycrab.NULL_AFFIX],
                affix_side="prefix",
            )
        )


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
        >>> sig2.get_final_entropy()
        1.0
        >>> print(sig2)
        ================================================== NULL=ed=ing

        add     want
        ------------------------
        want 2     add  1
        ------------------------

            Letters in words if unanalyzed:         31
                       Letters as analyzed:         12

        Final stem letter entropy: 1.000

        Number of stems: 2

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
        """Tests for signature equality."""
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
        """Tests for signature inequality."""
        return not self == other_signature

    def __str__(self):
        """Formats the signature for display."""

        lines = list()

        # Alphabetical list of affixes...
        lines.append("=" * 50 + " " +
                     "=".join(str(affix) for affix in sorted(self.affixes)))
        lines.append("")

        # Stop here if signature has no stems.
        if not self.stems:
            return "\n".join(lines)

        # 6 columns of left-aligned stems in alphabetical order...
        sorted_stems = sorted(self.stems)
        col_len = len(max(sorted_stems, key=len))
        for idx in range(0, len(sorted_stems), 6):
            lines.append("    ".join(stem + " " * (col_len-len(stem))
                                     for stem in sorted_stems[idx:idx+6]))
        lines.append("-" * 24)

        # 3x2 columns of stems+counts in decreasing count order...
        sorted_stems = sorted(sorted_stems, key=self.stems.get, reverse=True)
        stem_col_len = len(max(sorted_stems, key=len))
        count_col_len = len(str(self.stems[sorted_stems[0]])) + 4
        for idx in range(0, len(sorted_stems), 3):
            line = list()
            for stem in sorted_stems[idx:idx+3]:
                line.append(stem + " " * (stem_col_len-len(stem)))
                count = str(self.stems[stem])
                line.append(count + " " * (count_col_len-len(count)))
            lines.append(" ".join(line))
        lines.append("-" * 24)

        # Number of letters in words or as analyzed...
        letters_in_words = sum(len(st)+len(af) for st, af in self.parses)
        lines.append("\n    Letters in words if unanalyzed: %10i" 
                     % letters_in_words)
        lines.append("               Letters as analyzed: %10i" 
                     % (letters_in_words-self.robustness))

        # Final stem letter entropy...
        lines.append("\nFinal stem letter entropy: %.3f"
                     % self.get_final_entropy())

        # Number of stems.
        lines.append("\nNumber of stems: %i\n" % len(self.stems))

        return "\n".join(lines)

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

    def get_final_entropy(self, num_letters=1):
        """Compute entropy (in bits) over final stem letter sequences.

        Args:
            num_letters (int): length of final sequences (defaults to 1).

        Returns:
            float.

        Raises:
            ValueError: If signature contains stems shorter than num_letters.

        """
        for stem in self.stems:
            if len(stem) < num_letters:
                raise ValueError("Signature contains stems shorter than "
                                 "required number of letters for entropy "
                                 "calculation")
        counts = collections.Counter(stem[-num_letters] for stem in self.stems)
        return pycrab.utils.entropy(counts)
