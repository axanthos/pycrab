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

from builtins import range, dict
import collections
import inspect
from io import open
import os
import itertools
import re

from cached_property import cached_property
from pycrab.null_affix import NULLAffix
import pycrab.utils
from pycrab.utils import ImmutableDict, biograph

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"

MIN_NUM_STEMS = 2
"""Module-level constant for the min number of stems in a signature."""

MIN_STEM_LEN = 2
"""Module-level constant for the min number of letters in a stem."""

NUM_SEED_FAMILIES = 30
"""Module-level constant for the number of seed families to create."""

MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION = 100
"""Module-level constant for the minimal robustness required for a signature
to be considered for inclusion in a family."""

MIN_ENTROPY_FOR_BIPARSE_INCLUSION = 1.5
"""Module-level constant for the minimal edge entropy required for a signature
to be added to a biparse."""

AFFIX_DELIMITER = "="
"""Module-level constant for the delimiter symbol in affix strings."""

AFFIX_MARKER = ":"  # TODO: use to separate affix from disambiguation index
"""Module-level constant for the symbol that marks affixes when needed."""

TOKENIZATION_REGEX = r"\w+(?u)"
"""Module-level constant for the regex pattern used to tokenize text."""

LOWERCASE_INPUT = True
"""Module-level constant indicating wether input words should be lowercased."""

INPUT_ENCODING = "utf8"
"""Module-level constant for input file default encoding."""

NULL_AFFIX = NULLAffix()
"""Module-level constant representing the NULL affix."""


class Morphology(object):
    """A class for implementing an entire morphology in pycrab.

    The Morphology class has mainly two attributes, namely a set of suffixal
    signatures and a set of prefixal signatures. Stems, suffixes, and prefixes
    are read-only properties computed on the basis of the signatures, and so
    are suffixal and prefixal parses.

    Examples:

    In general, the user will want to learn a morphology based on some data,
    which can be stored in a text file, a string, or a list of words:

        >>> import pycrab
        >>> morphology = pycrab.Morphology()
        >>> morphology.learn_from_file(path_to_text_file)
        >>> morphology.learn_from_string("some text data")
        >>> morphology.learn_from_word_list(["a", "list", "of", "words"])

    All of these learning methods share the following optional arguments:

    * "lowercase_input" indicates whether the input words should be lowercased
      (defaults to True)

    * "min_stem_len" specifies the minimum number of letters that a stem can
      contain (defaults to 2)

    * "min_num_stems" specifies the minimum number of stems for creating a
      signature (defaults to 2)

    * "affix_side" indicates whether the learning process should build suffixal
      signatures of prefixal signatures (defaults to "suffix")

    Some of these learning methods have optional arguments of their own:
    learn_from_file can take an "encoding" argument which defaults to "utf8",
    and learn_from_string can take a "tokenization_regex" argument which
    defaults to r"\w+(?u)".

    There are mostly two ways of viewing the contents of a morphology once it
    has been been learnt. The serialize() method offers a synthetic view of
    the morphology, while the serialize_signatures() method displays the
    details of all signatures. Both methods can take an optional "affix_side"
    argument which defaults to "suffix" and indicates whether suffixal or
    prefixal signatures should be displayed

        >>> print(morphology.serialize())
        Number of stems:                                       4
        Number of signatures:                                  2
        Number of singleton signatures (one stem):             0
        Number of doubleton signatures (two stems):            2
        Total number of letters in stems                      11
        Total number of affix letters                          9
        Total number of letters in signatures                 20

        ------------------------------------------------------------------------------------------------------------
        Signature     Stem count   Robustness   Proportion of robustness   Running sum   Edge entropy   Example stem
        ------------------------------------------------------------------------------------------------------------
        NULL=ed=ing            2           19                      0.703         0.703            1.0   add
        ied=y                  2            8                      0.296           1.0            0.0   cr

        >>> print(morphology.serialize_signatures())
        ================================================== NULL=ed=ing

        add     want
        ------------------------
        add  2     want 1
        ------------------------

            Letters in words if unanalyzed:         31
                       Letters as analyzed:         12

        Final stem letter entropy: 1.000

        Number of stems: 2

        ================================================== ied=y

        cr    dr
        ------------------------
        cr 1     dr 1
        ------------------------

            Letters in words if unanalyzed:         16
                       Letters as analyzed:          8

        Final stem letter entropy: 0.000

        Number of stems: 2

        Lower level methods and attributes are available for users interested
        in developing learning algorithms (or, more generally, needing more
        fine-grained control over a morpology).

        >>> morphology = pycrab.Morphology(
        ...     pycrab.Signature(
        ...         stems=["want", "add", "add"],
        ...         affixes=[pycrab.NULL_AFFIX, "ed", "ing"],
        ...     ),
        ...     pycrab.Signature(
        ...         stems=["cr", "dr"],
        ...         affixes=["y", "ied"],
        ...     ),
        ...     pycrab.Signature(
        ...         stems=["do", "wind"],
        ...         affixes=["un", "re"],
        ...         affix_side="prefix",
        ...     ),
        ... )
        >>> morphology.add_signature(
        ...     stems=["make", "create"],
        ...     affixes=["re", pycrab.NULL_AFFIX],
        ...     affix_side="prefix",
        ... )
        >>> morphology.suffixal_stems
        {'want', 'dr', 'add', 'cr'}
        >>> morphology.prefixal_stems
        {'do', 'wind', 'create', 'make'}
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
        - check meaning of "total letter count in words" etc. in serialize()
        - add min_stem_length constraint in build_signatures?
        - find better names for serialization methods?
        - get_families/signatures return sets instead of lists?
        - document word biographies

    """

    def __init__(self, *signatures):
        """__init__ method for class Morphology.

        Args:
            *signatures (optional): comma-separated signatures

        """

        self.reset()
        for signature in signatures:
            if signature.affix_side == "prefix":
                self.prefixal_signatures[signature.affix_string] = signature
            else:
                self.suffixal_signatures[signature.affix_string] = signature

    def reset(self):
        """Reset all attributes of the morphology.

        Args: none.
        
        Returns: nothing.

        """
        self.word_counts = collections.Counter()

        self.prefixal_signatures = dict()
        self.prefixal_families = set()
        self.prefixal_protostems = collections.defaultdict(set)
        self.prefixal_word_biographies = collections.defaultdict(dict)
        self.prefixal_name_collisions = list()
        self.prefixal_analyses_run = list()

        self.suffixal_signatures = dict()
        self.suffixal_families = set()
        self.suffixal_protostems = collections.defaultdict(set)
        self.suffixal_word_biographies = collections.defaultdict(dict)
        self.suffixal_name_collisions = list()
        self.suffixal_analyses_run = list()

    def __eq__(self, other_morphology):
        """Tests for morphology equality."""

        if not isinstance(other_morphology, type(self)):
            return False
        if other_morphology.suffixal_signatures != self.suffixal_signatures:
            return False
        if other_morphology.prefixal_signatures != self.prefixal_signatures:
            return False
        return True

    def __ne__(self, other_morphology):
        """Tests for morphology inequality."""

        return not self == other_morphology

    def get_families(self, affix_side="suffix"):
        """Returns the list of suffixal or prefixal families.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            list of families.

        Todo: test

        """

        if affix_side == "prefix":
            return self.prefixal_families
        else:
            return self.suffixal_families

    def get_word_biographies(self, affix_side="suffix"):
        """Returns the dict of suffixal or prefixal word biographies.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            dict of word biographies (keys are words).

        """

        if affix_side == "prefix":
            return self.prefixal_word_biographies
        else:
            return self.suffixal_word_biographies

    def get_protostems(self, affix_side="suffix"):
        """Returns the dict of suffixal/prefixal protostems and continuations.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            dict of protostem continuations (keys are protostems, values are
            sets of strings).

        """

        if affix_side == "prefix":
            return self.prefixal_protostems
        else:
            return self.suffixal_protostems

    def get_signatures(self, affix_side="suffix"):
        """Returns the list of suffixal or prefixal signatures.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            list of signatures.

        """

        if affix_side == "prefix":
            return list(self.prefixal_signatures.values())
        else:
            return list(self.suffixal_signatures.values())

    def get_signature(self, affix_string, affix_side="suffix"):
        """Returns the Signature object corresponding to a given affix string.

        Args:
            affix_string (string): the affix string of the requested signature.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            a Signature object.

        Raises:
            ValueError: If there is no signature of the requested type matching
                the requested affix string.

        """

        try:
            if affix_side == "prefix":
                return self.prefixal_signatures[affix_string]
            else:
                return self.suffixal_signatures[affix_string]
        except KeyError:
            raise ValueError(("No %sal signature matches the requested "
                              + "affix string") % affix_side)

    def add_signature(self, stems, affixes, affix_side="suffix"):
        """Adds a signature to the morphology.

        Signatures are stored in a dict, where the key is the signature's
        affix string and the value is a Signature object.

        Args:
            stems (mapping or iterable): stems associated with this signature
                (with counts if arg is a dict).
            affixes (mapping or iterable): affixes associated with this
                signature (with counts if arg is a dict).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        signature = Signature(stems, affixes, affix_side)
        if affix_side == "prefix":
            self.prefixal_signatures[signature.affix_string] = signature
        else:
            self.suffixal_signatures[signature.affix_string] = signature

    def remove_signature(self, affix_string, affix_side="suffix"):
        """Removes a signature from the morphology.

            affix_string (str):
                the affix string if the signature to remove.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        if affix_side == "prefix":
            del(self.prefixal_signatures[affix_string])
        else:
            del(self.suffixal_signatures[affix_string])

    @property
    def suffixal_stems(self):
        """Construct a set of stems based on all suffixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self.get_stems()

    @property
    def prefixal_stems(self):
        """Construct a set of stems based on all prefixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self.get_stems(affix_side="prefix")

    def get_stems(self, affix_side="suffix"):
        """Construct a set of stems based on all signatures of a given type.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            set of strings.

        """

        stems = set()
        for signature in self.get_signatures(affix_side):
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

        return self.get_affixes()

    @property
    def prefixes(self):
        """Construct a set of prefixes based on all prefixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self.get_affixes(affix_side="prefix")

    def get_affixes(self, affix_side="suffix"):
        """Construct a set of affixes based on all signatures of a given type.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            set of strings.

        """

        affixes = set()
        for signature in self.get_signatures(affix_side):
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

        return self.get_parses()

    @property
    def prefixal_parses(self):
        """Construct a set of parses based on all prefixal signatures.

        Parses are pairs (prefix, stem).

        Args:
            none.

        Returns:
            set of tuples.

        """

        return self.get_parses(affix_side="prefix")

    def get_parses(self, affix_side="suffix"):
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
        for signature in self.get_signatures(affix_side):
            parses.update(signature.parses)
        return parses

    def get_name_collisions(self, affix_side="suffix"):
        """Returns the name collision counter for suffixes or prefixes.

        Keys are affixes and values are number of affixes with that name
        (if a collision has already occurred) .

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            list of strings.

        """

        if affix_side == "prefix":
            return self.prefixal_name_collisions
        else:
            return self.suffixal_name_collisions

    def get_analyses_list(self, affix_side="suffix"):
        """Returns the list of analyses run on suffixes or prefixes.

        Analyses are names of methods in this class.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            list of strings.

        """

        if affix_side == "prefix":
            return self.prefixal_analyses_run
        else:
            return self.suffixal_analyses_run

    def get_shadow_signatures(self, affix_side="suffix"):
        """Compute the set of shadow signatures of a given type.

        Shadow signatures are potentially spurious signatures that pycrab's
        learning algorithm discovers as a consequence of having discovered
        another signature which has two or more affixes starting with the same
        letter or sequence of letters.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            set of shadow signatures.

        """
        shadow_signatures = set()
        for signature in self.get_signatures(affix_side):
            shadow_signatures.update(signature.cast_shadow_signatures)
        return shadow_signatures

    def serialize(self, affix_side="suffix"):
        """Formats the morphology for synthetic display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        Todo: test

        """

        lines = list()

        # Select affix side.
        signatures = self.get_signatures(affix_side)
        if not signatures:
            return("Morphology contains no %sal signatures." % affix_side)
        if affix_side == "prefix":
            affixes = self.prefixes
            stems = self.prefixal_stems
        else:
            affixes = self.suffixes
            stems = self.suffixal_stems

        try:
            # Number of words.
            lines.append("%-45s %10i" % (
                "Number of words (corpus count):",
                sum(v for v in self.word_counts.values())
            ))

            # Total letter count in words.
            lines.append("%-45s %10i" % (
                "Total letter count in words:",
                sum(len(word) for word in self.word_counts)
            ))
        except AttributeError:
            lines.append("%-54s 0" % "Number of words (corpus count):")
            lines.append("%-54s 0" % "Total letter count in words:")

        # Number of stems.
        lines.append("%-45s %10i" % ("Number of stems:", len(stems)))

        # Number of signatures.
        lines.append("%-45s %10i" % ("Number of signatures:", len(signatures)))

        # Number of singleton and doubleton signatures...
        singleton = doubleton = 0
        for signature in signatures:
            if len(signature.stems) == 1:
                singleton += 1
            elif len(signature.stems) == 2:
                doubleton += 1
        lines.append("%-45s %10i" % (
            "Number of singleton signatures (one stem):",
            singleton,
        ))
        lines.append("%-45s %10i" % (
            "Number of doubleton signatures (two stems):",
            doubleton,
        ))

        # Total number of letters in stems.
        lines.append("%-45s %10i" % (
            "Total number of letters in stems",
            sum(len(stem) for stem in stems),
        ))

        # Total number of affix letters.
        lines.append("%-45s %10i" % (
            "Total number of affix letters",
            sum(len(affix) for affix in affixes),
        ))

        # Total number of letters in signatures.
        num_letters = 0
        for signature in signatures:
            num_letters += sum(len(stem) for stem in signature.stems)
            num_letters += sum(len(affix) for affix in signature.affixes)
        lines.append("%-45s %10i" % (
            "Total number of letters in signatures",
            num_letters,
        ))

        # Number of analyzed words...
        parses = self.get_parses(affix_side)
        lines.append("%-45s %10i" % ("Number of analyzed words:", len(parses)))

        # Total number of letters in analyzed words.
        lines.append("%-45s %10i" % (
            "Total number of letters in analyzed words:",
            sum(len(parse[0]) + len(parse[1]) for parse in parses),
        ))

        lines.append("")

        # Compute total robustness.
        total_robustness = sum(sig.robustness for sig in signatures)

        # Compute first and last column header length...
        max_affix_str_len = max(len(sig.affix_string) for sig in signatures)
        first_col_len = max(max_affix_str_len, len("Signature"))
        first_col_len += 2  # For potential shadow signatures...
        max_example_stem_len = max(len(sig.example_stem) for sig in signatures)
        last_col_len = max(max_example_stem_len, len("Example stem"))

        # Get list of shadow signatures.
        shadow_signatures = self.get_shadow_signatures(affix_side)

        # Define headers and corresponding content formats...
        headers = [
            "Stem count",
            "Robustness",
            "Proportion of robustness",
            "Running sum",
            "Edge entropy",
        ]
        formats = [
            "%{}i",
            "%{}i",
            "%{}.3f",
            "%{}.3f",
            "%{}.2f",
        ]

        # Construct header row...
        separator_len = 3
        divider_len = sum(len(h) for h in headers)
        divider_len += first_col_len + last_col_len
        divider_len += separator_len * (len(headers)+1)
        divider = "-" * divider_len
        header_row = ("%-"+str(first_col_len+separator_len)+"s") % "Signature"
        header_row += (" " * separator_len).join(headers)
        header_row += " " * separator_len
        header_row += ("%-"+str(last_col_len)+"s") % "Example stem"
        lines.extend([divider, header_row, divider])

        # Format each signature...
        running_sum = 0
        for signature in sorted(signatures,
                                key=lambda signature: signature.robustness,
                                reverse=True):
            proportion_of_robustness = signature.robustness / total_robustness
            running_sum += proportion_of_robustness
            vals = [
                len(signature.stems),
                signature.robustness,
                proportion_of_robustness,
                running_sum,
                signature.get_edge_entropy(),
            ]
            affix_string = signature.affix_string
            affix_string = pycrab.utils.format_if_shadow(affix_string,
                                                         shadow_signatures)
            val_len_formats = [(affix_string, first_col_len, "%-{}s")]
            val_len_formats.extend((vals[idx], len(headers[idx]), formats[idx])
                                    for idx in range(len(headers)))
            val_len_formats.append((signature.example_stem,
                                    last_col_len, "%-{}s"))
            cells = [my_format.format(length) % val
                     for val, length, my_format in val_len_formats]
            lines.append((" " * separator_len).join(cells))

        return "\n".join(lines) + "\n"

    def serialize_signatures(self, affix_side="suffix", order="robustness"):
        """Formats the signatures for detailed display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".
            order (string, optional): either "robustness" (default, decreasing)
                or "ascii".

        Returns:
            String.

        Todo: test

        """

        signatures = self.get_signatures(affix_side)
        if not signatures:
            return("Morphology contains no %sal signatures." % affix_side)
        if order == "ascii":
            signatures.sort(key=lambda signature: signature.affix_string)
        else:
            signatures.sort(key=lambda signature: signature.robustness,
                             reverse=True)
        return "\n".join(str(signature) for signature in signatures)

    def serialize_families(self, affix_side="suffix"):
        """Formats the families for detailed display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        Todo: test

        """

        families = self.get_families(affix_side)
        if not families:
            return("Morphology contains no %sal families." % affix_side)
        return "\n".join(str(family) for family in families)

    def serialize_stems_and_words(self, affix_side="suffix"):
        """Formats a list of stems and related words for display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        Todo: test

        """

        lines = list()

        # Get union of stems and words...
        stems = self.get_stems(affix_side)
        entries = stems.union(self.word_counts.keys())
        if not entries:
            return("Morphology contains no words.")

        # Get continuations of stems...
        parses = self.get_parses(affix_side)
        continuations = collections.defaultdict(set)
        analyzed_words = set()
        if affix_side == "prefix":
            for prefix, stem in parses:
                continuations[stem].add(prefix)
                analyzed_words.add(prefix + stem)
        else:
            for stem, suffix in parses:
                continuations[stem].add(suffix)
                analyzed_words.add(stem + suffix)

        # Format each stem or word...
        for entry in sorted(entries):
            if entry in stems:
                if affix_side == "prefix":
                    lines.append(entry + "\t" + "\t".join(
                                 c + entry for c in sorted(continuations[entry])
                                 ))
                else:
                    lines.append(entry + "\t" + "\t".join(
                                 entry + c for c in sorted(continuations[entry])
                                 ))
            elif entry not in analyzed_words:
                lines.append(entry + "*")

        return "\n".join(lines) + "\n"

    def serialize_word_biographies(self, affix_side="suffix"):
        """Formats word biographies for display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        Todo: test

        """

        lines = list()
        for word, biography in sorted(
                self.get_word_biographies(affix_side).items()):
            lines.append(word + ":")
            for func in self.get_analyses_list(affix_side):
                lines.append("\t" + func + ":")
                try:
                    for parse in sorted(biography[func]):
                        lines.append("\t\t%s %s" % parse)
                except KeyError:
                    lines.append("\t\tunanalyzed")
        return "\n".join(lines)

    def serialize_protostems(self, affix_side="suffix"):
        """Formats protostems and continuations for display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        Todo: test

        """

        lines = list()
        for protostem, continuations in sorted(
                self.get_protostems(affix_side).items()):
            lines.append(protostem + ": " + ", ".join(sorted(str(c)
                                                     for c in continuations)))
        return "\n".join(lines)

    def get_stem_and_affix_count(self, stems, affixes, affix_side="suffix"):
        """Return frequency counts for selected affixes and stems.

        Args:
            stems (set):
                set of stems
            affixes (set):
                set of affixes
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            pair of collection.Counter object (stem and affix count).

        """

        stem_counts = collections.Counter()
        affix_counts = collections.Counter()
        for stem in stems:
            for affix in affixes:
                word = stem+affix if affix_side == "suffix" else affix+stem
                word_count = self.word_counts[word]
                stem_counts[stem] += word_count
                affix_counts[affix] += word_count
        return stem_counts, affix_counts

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

        if affix_side == "prefix":
            self.prefixal_signatures = dict()
        else:
            self.suffixal_signatures = dict()

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
        signatures = set()
        for affixes, stems in stem_sets.items():
            if len(stems) >= min_num_stems:     # Require min number of stems.
                if self.word_counts:
                    stem_counts, affix_counts = self.get_stem_and_affix_count(
                        stems, affixes, affix_side=affix_side)
                    self.add_signature(stem_counts, affix_counts, affix_side)
                else:   # If no word counts are available yet...
                    self.add_signature(stems, affixes, affix_side)

        return len(signatures)

    @biograph
    def find_signatures1(self, min_stem_len=MIN_STEM_LEN,
                         min_num_stems=MIN_NUM_STEMS, affix_side="suffix"):
        """Find initial signatures (using Goldsmith's Lxa-Crab algorithm).

        Args:
            min_stem_len (int, optional): minimum number of letters required in
                a stem (default is MIN_STEM_LEN).
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: test.

        """

        protostems = set()

        # Initialize morphology.
        self.reset()

        # Invert words if needed (if affix side is prefix), then sort them...
        if affix_side == "suffix":
            sorted_words = sorted(list(word_counts))
        else:
            sorted_words = sorted(word[::-1] for word in word_counts)
            
        # For each pair of successive words (in alphabetical order)...
        for idx in range(len(sorted_words)-1):

            # Add longest common prefix to protostems (if long enough)...
            protostem = os.path.commonprefix(sorted_words[idx:idx+2])
            if len(protostem) >= min_stem_len:
                protostems.add(protostem)

        # List all possible continuations of each protostem...
        continuations = collections.defaultdict(list)
        for word in sorted_words:
            for prefix_len in range(min_stem_len, len(word)+1):
                prefix = word[:prefix_len]
                if prefix in protostems:
                    continuations[prefix].append(word[prefix_len:])

        # Find all stems associated with each continuation list...
        protostem_lists = collections.defaultdict(set)
        for protostem, continuation in continuations.items():
            protostem_lists[tuple(sorted(continuation))].add(protostem)

        # For each continuation list...
        for continuations, protostems in protostem_lists.items():

            # If affix side is prefix, reverse stems and continuations...
            if affix_side == "prefix":
                protostems = [protostem[::-1] for protostem in protostems]
                continuations = [cont[::-1] for cont in continuations]

            # Replace empty affix with NULL_AFFIX.
            continuations = [cont if len(cont) else NULL_AFFIX
                             for cont in continuations]

            # If continuation list has min_num_stems stems or more...
            if len(protostems) >= min_num_stems:

                # Get stem and affix counts...
                stem_counts, affix_counts = self.get_stem_and_affix_count(
                    protostems, continuations, affix_side=affix_side)

                # Create and store signature.
                self.add_signature(stems=stem_counts, affixes=affix_counts,
                                   affix_side=affix_side)

            # Store remaining protostems for later analysis...
            else:
                self.get_protostems(affix_side).update({p: set(continuations)
                                                        for p in protostems})

    def create_families(self, num_seed_families=NUM_SEED_FAMILIES,
                        min_robustness=MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
                        affix_side="suffix"):
        """Create families; each family has a nucleus signature, which comes
           from the most robust signatures, and it finds other signatures which
           are supersets of the nucleus.

        Args:
            num_seed_families (int, optional): the number of seed families to
                create (defaults to NUM_SEED_FAMILIES).
            min_robustness (float, optional): the minimal robustness for
                a signature to be added to a family (defaults to
                MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: test.

        """

        # Sort signatures by decreasing robustness.
        signatures = self.get_signatures(affix_side)
        signatures.sort(key=lambda signature: signature.robustness,
                        reverse=True)

        # Create families based on the N most robust signatures...
        families = list()
        actual_num_seed_families = min(NUM_SEED_FAMILIES, len(signatures))
        for nucleus in signatures[:actual_num_seed_families]:
            families.append(Family(nucleus.affix_string, morphology=self,
                            affix_side=affix_side))

        # Sort families by decreasing affix length.
        families.sort(key=lambda family:
                      len(family.nucleus.split(AFFIX_DELIMITER)), reverse=True)

        # For each remaining signature...
        for signature in signatures[actual_num_seed_families:]:

            # Skip if its robustness is below threshold.
            if signature.robustness < min_robustness:
                continue

            # Add it to the family with the largest nucleus that it contains...
            for family in families:
                if signature.contains(family.nucleus):
                    family.children.add(signature.affix_string)
                    break

        # Store families in morphology...
        if affix_side == "prefix":
            self.prefixal_families = families
        else:
            self.suffixal_families = families

    @biograph
    def widen_signatures(self, affix_side="suffix"):
        """Expand existing signatures with protostems that can be continued
        by all their affixes. In case of ambiguity, protostems are added to
        the longest possible signature.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: test.

        """

        # Get current parses and protostems.
        parses = self.get_parses(affix_side)
        protostems = self.get_protostems(affix_side)

        # Initialize list of protostems previously added to a signature.
        previously_added = set()

        # For each signature sorted by number of affixes then robustness...
        signatures = self.get_signatures(affix_side)
        signatures.sort(key=lambda s: s.robustness, reverse=True)
        signatures.sort(key=lambda s: len(s.affixes), reverse=True)
        for signature in signatures:
            affixes = set(signature.affixes)

            # For all unanalyzed protostems...
            for protostem, continuations in protostems.items():

                # Skip if previously added to signature...
                if protostem in previously_added:
                    continue

                # If this protostem can have all affixes in this signature...
                if affixes.issubset(continuations):

                    # Create new parses and remove them from unanalyzed stuff...
                    for affix in affixes:
                        parses.add((affix, protostem) if affix_side == "prefix"
                                   else (protostem, affix))
                        protostems[protostem].remove(affix)

                    # Flag protostem as previously added to a signature...
                    previously_added.add(protostem)

        # Update signatures to reflect parses.
        self.build_signatures(parses, affix_side)

    def split_affixes(self, affix_side="suffix"):
        """Split affixes based on the observation of multiply analyzed words.

        This method relies crucially on a particular data structure called
        a "biparse". A biparse connects two signatures by means of a string:
        a signature with shorter stems, e.g. "bowl" and "record" (with suffixes
        NULL=ed=ing=ings=s), and a signature with longer stems, e.g. "bowling"
        and "recording" (with suffixes NULL=s); in this example, the connecting
        string, or "string difference", is "ing", which means that there exist
        one or more words that can be parsed by both signatures in the biparse,
        each of them yielding a pair (short stem, long stem), where the long
        stem is the short stem plus the string difference "ing". E.g. the word
        "bowling" can be analyzed as the shorter stem "bowl" in the signature
        NULL=ed=ing=ings=s or as the long stem "bowling" in the signature
        NULL=s, and "bowling" (long stem) is "bowl" (short stem) + "ing" (string
        difference), and likewise for word "recording".

        What the method learns from having found a biparse is that those affixes
        of the short stem signature that begin with the string difference can be
        reanalyzed as sequences of 2 affixes, namely the string difference
        itself and a residue which is often an affix in the long stem signature.
        In our example, "ing" and "ings" in NULL=ed=ing=ings=s are reanalyzed as
        "ing" + NULL and "ing" + "s". In addition, if the string difference
        corresponds to an existing affix, we do not make the assumption that
        they are one an the same at this point; rather, we disambiguate the
        newly discovered affix by adding an integer to it, e.g. "ing2". Thus,
        the short stem signature NULL=ed=ing=ings=s is in effect replaced by a
        new short stem signature NULL=ed=ing2=s, while "ing2" becomes a stem in
        a signature whose affixes are the "residues" mentioned above, i.e. the
        second components in the sequence of affixes resulting from the
        reanalysis of affixes of the short stem signature, namely NULL and "s".

        The discovered rule can be summarized as [NULL=ed=ing=s]_ing ==> NULL_s,
        which means that words that have the affix "ing" found in the signature
        NULL=ed=ing=s can have NULL or "s" as a second affix (e.g. "bowlings"
        can be parsed as "bowl" + "ing2" + "s".

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: test.

        """

        # Get all analyses (stem + signature) associated with each word...
        word_to_analyses = collections.defaultdict(set)
        for sig in self.get_signatures(affix_side):
            for parse in sig.parses:
                stem = parse[1] if affix_side == "prefix" else parse[0]
                word_to_analyses["".join(parse)].add((stem, sig.affix_string))

        # Initialize mapping from biparses to sets of stems.
        biparse_to_stems = collections.defaultdict(set)

        # For each word that has more than 1 analysis...
        for word, analyses in word_to_analyses.items():
            if len(analyses) > 1:

                # For each pair of analyses of this word...
                pairs_of_analyses = itertools.combinations(sorted(analyses,
                        key=lambda x: len(x[0])), 2)
                for pair_of_analyses in pairs_of_analyses:
                    short_stem, short_stem_sig = pair_of_analyses[0]
                    long_stem, long_stem_sig = pair_of_analyses[1]

                    # If edge entropy of longer stem analysis exceeds threshold...
                    long_stem_sig_object = self.get_signature(long_stem_sig,
                                                              affix_side)
                    if long_stem_sig_object.get_edge_entropy()    \
                            >= MIN_ENTROPY_FOR_BIPARSE_INCLUSION:

                        # Compute diff and associate short stem to biparse...
                        if affix_side == "suffix":
                            diff = long_stem[len(short_stem):]
                        else:
                            diff = long_stem[:-len(short_stem)]
                        key = diff, short_stem_sig, long_stem_sig
                        biparse_to_stems[key].add(short_stem)

                        # TODO: store for later output
                        print("%s\t"*5 % (diff, short_stem, short_stem_sig,
                                          long_stem, long_stem_sig))

        # Get current state of parses, word biographies and name collisions...
        parses = self.get_parses(affix_side)
        biographies = self.get_word_biographies(affix_side)
        collisions = self.get_name_collisions(affix_side)

        # Get the name of this function (to update biographies).
        func = inspect.currentframe().f_code.co_name

        # For each stored biparse and associated short stems
        for (biparse, short_stems) in biparse_to_stems.items():
            diff, short_stem_sig, long_stem_sig = biparse

            # Disambiguate diff if needed and add affix marker...
            disamb_diff = diff
            if collisions[diff] or diff in self.get_affixes(affix_side):
                disamb_diff += "%i" % (collisions[diff]+2)
            collisions[diff] += 1
            if affix_side == "prefix":
                disamb_diff += AFFIX_MARKER
            else:
                disamb_diff = AFFIX_MARKER + disamb_diff

            # Build new short and long stem signatures...
            short_stem_sig_object = self.get_signature(short_stem_sig, affix_side)
            long_stem_sig_object = self.get_signature(long_stem_sig, affix_side)
            new_short_stem_sig = {diff}
            new_long_stem_sig = set(long_stem_sig_object.affixes)
            for affix in short_stem_sig_object.affixes:
                if affix == diff:
                    new_long_stem_sig.add(NULL_AFFIX)
                elif affix_side == "suffix" and affix.startswith(diff):
                    new_long_stem_sig.add(affix[len(diff):])
                elif affix_side == "prefix" and affix.endswith(diff):
                    new_long_stem_sig.add(affix[:-len(diff)])
                else:
                    new_short_stem_sig.add(affix)

            # TODO: Store for later output
            print("[%s]_%s\t==>\t%s\t%s\t%s\t%s" % ((
                AFFIX_DELIMITER.join(str(af) for af in sorted(new_short_stem_sig)),
                diff,
                AFFIX_DELIMITER.join(str(af) for af in sorted(new_long_stem_sig)),
                short_stem_sig,
                long_stem_sig,
                short_stems,
            )))

            # Initialize dict for storing rewrite rules (for biographies).
            rewrite = dict()

            # Utility unction for switching morphemes depending on affix side...
            def switch_if_needed(my_tuple, affix_side="suffix"):
                if affix_side == "prefix":
                    return tuple(reversed(my_tuple))
                else:
                    return my_tuple

            # Create new parse for diff + each affix in new long stem sig...
            for affix in new_long_stem_sig:
                new_parse = switch_if_needed((disamb_diff, affix), affix_side)
                parses.add(new_parse)
                print("1: added parse", *new_parse)

                # Store corresponding rewrite rule (for biographies)
                to_rewrite = affix+diff if affix_side == "prefix" else diff+affix
                rewrite[to_rewrite] = str(new_parse[0]) + " " + str(new_parse[1])
                print("new rewrite rule:", to_rewrite, "==>", rewrite[to_rewrite])

            # For each short stem associated with this biparse...
            for stem in short_stems:

                # Create new parse for stem + disambiguated diff...
                new_parse = switch_if_needed((stem, disamb_diff), affix_side)
                parses.add(new_parse)
                print("2: added parse", *new_parse)

                # Discard all parses in long stem signature...
                for affix in long_stem_sig_object.affixes:
                    stem_and_diff = "".join(switch_if_needed((stem, diff),
                                                             affix_side))
                    old_parse = switch_if_needed((stem_and_diff, affix),
                                                 affix_side)
                    parses.discard(old_parse)
                    print("3: discarded parse", *old_parse)

                # In short stem signature, discard all parses whose suffix
                # starts with diff (or whose prefix ends with diff)...
                for affix in short_stem_sig_object.affixes:
                    if ((affix_side == "suffix" and affix.startswith(diff))
                        or (affix_side == "prefix" and affix.endswith(diff))):
                        old_parse = switch_if_needed((stem, affix), affix_side)
                        parses.discard(old_parse)
                        print("4: discarded parse", *old_parse)

                        # Apply rewrite rules and update relevant biographies...
                        affix_seq = rewrite[affix].replace(AFFIX_MARKER, "")
                        to_rewrite = affix+stem if affix_side == "prefix"   \
                                     else stem+affix
                        new_analysis = switch_if_needed((stem, affix_seq),
                                                        affix_side)
                        biographies[to_rewrite][func] = {new_analysis}

        # Update signatures to reflect parses.
        self.build_signatures(parses, affix_side)

        # Update remaining word biographies and mark this analysis as run...
        analyses = self.get_analyses_list(affix_side)
        for word in biographies:
            if func not in biographies[word]:
                biographies[word][func] = biographies[word][analyses[-1]]
        analyses.append(func)

    def learn_from_wordlist(self, wordlist, lowercase_input=LOWERCASE_INPUT,
                            min_stem_len=MIN_STEM_LEN,
                            min_num_stems=MIN_NUM_STEMS,
                            num_seed_families=NUM_SEED_FAMILIES,
                            min_robustness=MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
                            affix_side="suffix"):
        """Learn morphology based on wordlist.

        Args:
            wordlist (list of strings): list of words, possibly repeated
            lowercase_input (bool, optional): indicates whether input words
                should be lowercased (default is LOWERCASE_INPUT).
            min_stem_len (int, optional): minimum number of letters required in
                a stem (default is MIN_STEM_LEN).
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).
            num_seed_families (int, optional): the number of seed families to
                create (defaults to NUM_SEED_FAMILIES).
            min_robustness (float, optional): the minimal robustness for
                a signature to be added to a family (defaults to
                MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: figure out how we want to call the other learning functions than
        find_signature1 for both affix sides (like we do for find_signature1).
        
        """

        # Lowercase words if needed...
        if lowercase_input:
            wordlist = [word.lower() for word in wordlist]

        # Count words and store word counts as attribute.
        self.word_counts = collections.Counter(wordlist)

        # Find suffixal signatures.
        self.find_signatures1(min_stem_len, min_num_stems)

        # Find prefixal signatures.
        self.find_signatures1(min_stem_len, min_num_stems,
                              affix_side="prefix")
        
        # Widen signatures.
        self.widen_signatures(affix_side)

        # Split affixes.
        self.split_affixes(affix_side)

        # Create signature families.
        self.create_families(num_seed_families, min_robustness, affix_side)


    def learn_from_string(self, input_string,
                          tokenization_regex=TOKENIZATION_REGEX,
                          lowercase_input=LOWERCASE_INPUT,
                          min_stem_len=MIN_STEM_LEN,
                          min_num_stems=MIN_NUM_STEMS,
                          num_seed_families=NUM_SEED_FAMILIES,
                          min_robustness=MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
                          affix_side="suffix"):
        """Learn morphology based on a single, unsegmented string.

        NB: tokenization is done with a regular expression.

        Args:
            input_string (string): the text to learn from.
            tokenization_regex (string, optional): regular expression used for
                tokenizing input text (default is TOKENIZATION_REGEX).
            lowercase_input (bool, optional): indicates whether input words
                should be lowercased (default is LOWERCASE_INPUT).
            min_stem_len (int, optional): minimum number of letters required in
                a stem (default is MIN_STEM_LEN).
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).
            num_seed_families (int, optional): the number of seed families to
                create (defaults to NUM_SEED_FAMILIES).
            min_robustness (float, optional): the minimal robustness for
                a signature to be added to a family (defaults to
                MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        # Split content into words...
        words = re.findall(tokenization_regex, input_string)

        self.learn_from_wordlist(words, lowercase_input, min_stem_len,
                                 min_num_stems, num_seed_families,
                                 min_robustness, affix_side=affix_side)

    def learn_from_file(self, input_file_path, encoding=INPUT_ENCODING,
                        tokenization_regex=TOKENIZATION_REGEX,
                        lowercase_input=LOWERCASE_INPUT,
                        min_stem_len=MIN_STEM_LEN, min_num_stems=MIN_NUM_STEMS,
                        num_seed_families=NUM_SEED_FAMILIES,
                        min_robustness=MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
                        affix_side="suffix"):
        """Learn morphology based on a text file.

        NB: tokenization is done with a regular expression.

        Args:
            input_file_path (string or pathlib.Path object): text file path.
            encoding (string, optional): input file encoding (default is
                INPUT_ENCODING).
            tokenization_regex (string, optional): regular expression used for
                tokenizing input text (default is TOKENIZATION_REGEX).
            lowercase_input (bool, optional): indicates whether input words
                should be lowercased (default is LOWERCASE_INPUT).
            min_stem_len (int, optional): minimum number of letters required in
                a stem (default is MIN_STEM_LEN).
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).
            num_seed_families (int, optional): the number of seed families to
                create (defaults to NUM_SEED_FAMILIES).
            min_robustness (float, optional): the minimal robustness for
                a signature to be added to a family (defaults to
                MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        # Attempt to open and read file...
        input_file = open(input_file_path, encoding=encoding, mode="r")
        content_lines = input_file.readlines()
        input_file.close()

        # Remove lines starting with '#'
        content_lines = [l for l in content_lines if not l.startswith("#")]

        self.learn_from_string("\n".join(content_lines), tokenization_regex,
                               lowercase_input, min_stem_len,
                               min_num_stems, num_seed_families,
                               min_robustness, affix_side=affix_side)

    @biograph
    def _add_test_signatures(self):
        """"Add signatures to morphology for testing purposes."""
        self.add_signature(
            stems=["want", "add", "add"],
            affixes=[pycrab.NULL_AFFIX, "ed", "ing"],
        )
        self.add_signature(
            stems=["cr", "dr"],
            affixes=["y", "ied"],
        )
        self.add_signature(
            stems=["do", "wind"],
            affixes=["un", "re"],
            affix_side="prefix",
        )
        self.add_signature(
            stems=["make", "create"],
            affixes=["re", pycrab.NULL_AFFIX],
            affix_side="prefix",
        )


class Signature(tuple):
    """A class for implementing a signature in pycrab.

    The Signature class is at the heart of pycrab's morphology representation
    and learning procedures. A signature has an "affix side" (either "suffix",
    the default, or "prefix"), as well as a dict of stems and a dict of
    affixes, each of which has integer counts as values. Stems and affixes can
    be initialized either with dicts or with other iterables such as lists and
    sets. Signature objects are immutable.

    Examples:
        >>> import pycrab
        >>> sig = pycrab.Signature(
        ...     stems=["want", "want", "add"],
        ...     affixes={pycrab.NULL_AFFIX: 6, "ing": 8, "ed": 6},
        ... )
        >>> sig.stems
        {'want': 2, 'add': 1}
        >>> sig.example_stem
        'want'
        >>> sig.affixes
        {'ing': 8, NULL: 6, 'ed': 6}
        >>> sig.affix_string
        'NULL=ed=ing'
        >>> sig.robustness
        19
        >>> sig.parses
        {('add', NULL), ('add', 'ed'), ('add', 'ing'), ('want', 'ing'),
        ('want', 'ed'), ('want', NULL)}
        >>> sig.get_edge_entropy()
        1.0
        >>> print(sig.affix_string)
        NULL=ed=ing
        >>> print(sig)
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

    def __new__(cls, stems, affixes, affix_side="suffix"):
        """__new__ method for class Signature.

        Args:
            stems (mapping or iterable): stems associated with this signature
                (with counts if arg is a dict).
            affixes (mapping or iterable): affixes associated with this
                signature (with counts if arg is a dict).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        """
        return tuple.__new__(cls, (ImmutableDict(stems),
                                   ImmutableDict(affixes), affix_side))

    @property
    def stems(self):
        """Read-only accessor for the stems attribute."""
        return tuple.__getitem__(self, 0)

    @property
    def affixes(self):
        """Read-only accessor for the affixes attribute."""
        return tuple.__getitem__(self, 1)

    @property
    def affix_side(self):
        """Read-only accessor for the affix_side attribute."""
        return tuple.__getitem__(self, 2)

    def __hash__(self):
        """Hashing function for signature objects."""
        return hash(tuple(sorted(self.affixes)))

    def __str__(self):
        """Formats the signature for display."""

        lines = list()

        # Alphabetical list of affixes...
        lines.append("=" * 50 + " " + self.affix_string)
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
                     % self.get_edge_entropy())

        # Number of stems.
        lines.append("\nNumber of stems: %i\n" % len(self.stems))

        return "\n".join(lines)

    def contains(self, affix_string):
        """Indicates if all the affixes of another signature are in this one.

        Args:
            signature (string): affix string of the other signature.

        Returns:
            bool.

        """
        return set(str(affix) for affix in self.affixes)    \
               >= set(affix_string.split(AFFIX_DELIMITER))

    @cached_property
    def affix_string(self):
        """Returns a string with the signature's sorted affixes.

        Args:
            none.

        Returns:
            string.

        """
        return self._compute_affix_string()

    def _compute_affix_string(self):
        """Construct a string with the signature's sorted affixes.

        Args:
            none.

        Returns:
            string.

        """

        return AFFIX_DELIMITER.join(str(affix).replace(AFFIX_MARKER, "")
                                    for affix in sorted(self.affixes))

    @cached_property
    def example_stem(self):
        """Returns the signature's most frequent stem.

        Args:
            none.

        Returns:
            string.

        """
        return self._compute_example_stem()

    def _compute_example_stem(self):
        """Returns the signature's most frequent stem.

        Args:
            none.

        Returns:
            string.

        """

        return max(self.stems, key=self.stems.get)

    @cached_property
    def robustness(self):
        """Returns the robustness of the signature.

        Robustness is the number of letters saved by a signature, which equals
        the sum of the lengths of all words covered by the signature, minus the
        sum of the lengths of stems, minus the sum of the lengths of affixes.

        Args:
            none.

        Returns:
            int.

        """
        return self._compute_robustness()

    def _compute_robustness(self):
        """Computes the robustness of the signature.

        Args:
            none.

        Returns:
            int.

        """
        saved_stem_length = len("".join(self.stems)) * (len(self.affixes)-1)
        saved_affix_length = len("".join(self.affixes)) * (len(self.stems)-1)
        return saved_stem_length + saved_affix_length

    @cached_property
    def parses(self):
        """Construct a set of parses using the signature's stems and affixes.

        Parses are pairs (prefix, stem) or (stem, suffix).

        Args:
            none.

        Returns:
            set of tuples.

        """
        return self._compute_parses()

    def _compute_parses(self):
        """Construct a set of parses using the signature's stems and affixes.

        Args:
            none.

        Returns:
            set of tuples.

        """

        if self.affix_side == "suffix":
            return set(itertools.product(self.stems, self.affixes))
        return set(itertools.product(self.affixes, self.stems))

    def get_edge_entropy(self, num_letters=1):
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
        counts = collections.Counter(stem[-num_letters:] for stem in self.stems)
        return pycrab.utils.entropy(counts)

    @cached_property
    def cast_shadow_signatures(self):
        """Compute the set of shadow signatures cast by this signature.

        Shadow signatures are potentially spurious signatures that pycrab's
        learning algorithm discovers as a consequence of having discovered
        another signature which has two or more affixes starting with the same
        letter or sequence of letters.

        Args: none.

        Returns:
            set of cast shadow signatures.

        """
        return self._compute_cast_shadow_signatures()

    def _compute_cast_shadow_signatures(self):
        """Compute the set of shadow signatures cast by this signature.

        Shadow signatures are potentially spurious signatures that pycrab's
        learning algorithm discovers as a consequence of having discovered
        another signature which has two or more affixes starting with the same
        letter or sequence of letters.

        Args: none.

        Returns:
            set of cast shadow signatures.

        Todo:
            find a way to predict on=ng=ngs=ive from ion=ing=ings=ive

        """
        cast_signatures = set()
        for pos in range(max(len(affix) for affix in self.affixes)):
            affix_beginnings = set(affix[0:pos] for affix in self.affixes
                                   if len(affix) > pos)
            for affix_beginning in affix_beginnings:
                letter_types_at_pos = set()
                considered_affixes = [affix for affix in self.affixes
                                      if affix.startswith(affix_beginning)
                                      and len(affix) > pos]
                letter_types_at_pos = set(affix[pos]
                                          for affix in considered_affixes)
                if affix_beginning in self.affixes:
                    considered_affixes.append(NULL_AFFIX)
                    letter_types_at_pos.add(str(NULL_AFFIX))
                if len(letter_types_at_pos) == len(considered_affixes) > 1:
                    cast_signatures.add(AFFIX_DELIMITER.join(l for l in
                                        sorted(letter_types_at_pos)))
        return cast_signatures


class Family(object):
    """A class for implementing a family of signature in pycrab.

    A family is a set of signatures related to a single nucleus signature. All
    signatures in a family contain the nucleus, i.e. they are supersets of the
    nucleus. Affixes contained in the superset signatures but not in the
    nucleus are called satellite affixes.

    Todo:
        Examples
        Tests

    """

    def __init__(self, nucleus, morphology, children=None,
                 affix_side="suffix"):
        """__init__ method for class Family.

        Args:
            nucleus (string): affix string of the family's nucleus signature.
            morphology (Morphology): a reference to the morphology containing
                this family.
            children (iterable of signatures, optional): signatures that
                 contain the family's nucleus (defaults to empty set).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        """
        self.nucleus = nucleus
        self.morphology = morphology
        self.children = set(children if children else list())
        self.affix_side = affix_side

    def __str__(self):
        """Formats the family for display."""

        lines = ["=" * 50]

        # Get shadow signatures' affix strings.
        shadow_sigs = self.morphology.get_shadow_signatures(self.affix_side)

        # Nucleus signature.
        lines.append("Nucleus: " +
                     pycrab.utils.format_if_shadow(self.nucleus, shadow_sigs))

        # Satellite affix counts...
        lines.append("Satellite affixes:")
        satellite_affix_counts = self.get_satellite_affix_counts()
        for item in sorted(satellite_affix_counts.items(),
                           key=lambda item: item[1], reverse=True):
            lines.append("\t%s\t%s" % item)
        if not satellite_affix_counts:
            lines.append("\tnone")

        # Child signatures..
        lines.append("Child signatures:")
        lines.extend("\t" + pycrab.utils.format_if_shadow(child, shadow_sigs)
                     for child in self.children)
        if not self.children:
            lines.append("\tnone")

        return "\n".join(lines) + "\n"

    def get_satellite_affix_counts(self):
        """Returns the number of stems associated with each satellite affix.

        Args: none.

        Returns:
            dictionary of satellite affix counts.

        Todo: test

        """

        nuclei_affixes = self.nucleus.split(AFFIX_DELIMITER)
        affix_counts = collections.Counter()
        for affix_string in self.children:
            signature = self.morphology.get_signature(affix_string,
                                                      self.affix_side)
            for affix in affix_string.split(AFFIX_DELIMITER):
                if affix not in nuclei_affixes:
                    affix_counts[affix] += len(signature.stems)
        return affix_counts
