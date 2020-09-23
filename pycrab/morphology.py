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

from io import open
from builtins import range, dict
import collections
import itertools
import re
import os

from cached_property import cached_property

import pycrab.utils
from pycrab.null_affix import NULLAffix
from pycrab.utils import ImmutableDict

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

AFFIX_DELIMITER = "="
"""Module-level constant for the delimiter symbol in affix strings."""

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

    The Morphology class has two attributes, namely a set of suffixal
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
        - store protostems
        - add min_stem_length constraint in build_signatures?
        - find better names for serialization methods?

    """

    def __init__(self, *signatures):
        """__init__ method for class Morphology.

        Args:
            *signatures (optional): comma-separated signatures

        """

        self.prefixal_signatures = dict()
        self.suffixal_signatures = dict()
        for signature in signatures:
            if signature.affix_side == "prefix":
                self.prefixal_signatures[signature.affix_string] = signature
            else:
                self.suffixal_signatures[signature.affix_string] = signature

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
            
        Todo: test

        """

        try:
            if affix_side == "prefix":
                return self.prefixal_signatures[affix_string]
            else:
                return self.suffixal_signatures[affix_string]
        except KeyError:
            raise ValueError("No %sal signature matches the requested "
                             + "affix string " % affix_side)

    def add_signature(self, stems, affixes, affix_side="prefix"):
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

        Todo: test

        """
        signature = Signature(stems, affixes, affix_side)
        if affix_side == "prefix":
            self.prefixal_signatures[signature.affix_string] = signature
        else:
            self.suffixal_signatures[signature.affix_string] = signature


    def serialize(self, affix_side="suffix"):
        """Formats the morphology for synthetic display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

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
        parses = self._get_parses(affix_side)
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
        max_example_stem_len = max(len(sig.example_stem) for sig in signatures)
        last_col_len = max(max_example_stem_len, len("Example stem"))

        # Define headers and corresponding content formats...
        headers = [
            "Stem count",
            "Robustness",
            "Proportion of robustness",
            "Running sum",
            "Edge entropy",
        ]
        formats = [
            "%{}s",
            "%{}s",
            "%{}.5s",
            "%{}.5s",
            "%{}.4s",
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
            val_len_formats = [(signature.affix_string, first_col_len, "%-{}s")]
            val_len_formats.extend((vals[idx], len(headers[idx]), formats[idx])
                                    for idx in range(len(headers)))
            val_len_formats.append((signature.example_stem,
                                    last_col_len, "%-{}s"))
            cells = [my_format.format(length) % val
                     for val, length, my_format in val_len_formats]
            lines.append((" " * separator_len).join(cells))

        return "\n".join(lines)

    def serialize_signatures(self, affix_side="suffix"):
        """Formats the signatures for detailed display.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns:
            String.

        """

        signatures = self.get_signatures(affix_side)
        if not signatures:
            return("Morphology contains no %sal signatures." % affix_side)
        lines = list()
        for signature in sorted(signatures,
                                key=lambda signature: signature.robustness,
                                reverse=True):
            lines.append(str(signature))
        return "\n".join(lines)

    @property
    def suffixal_stems(self):
        """Construct a set of stems based on all suffixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self._get_stems()

    @property
    def prefixal_stems(self):
        """Construct a set of stems based on all prefixal signatures.

        Args:
            none.

        Returns:
            set of strings.

        """

        return self._get_stems(affix_side="prefix")

    def _get_stems(self, affix_side="suffix"):
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
        for signature in self.get_signatures(affix_side):
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
        signatures = set()
        for affixes, stems in stem_sets.items():
            if len(stems) >= min_num_stems:     # Require min number of stems.
                signatures.add(Signature(stems, affixes, affix_side))

        # Update dict of signatures in morphology...
        if affix_side == "prefix":
            self.prefixal_signatures = dict()
            for signature in signatures:
                self.prefixal_signatures[signature.affix_string] = signature
        else:
            self.suffixal_signatures = dict()
            for signature in signatures:
                self.suffixal_signatures[signature.affix_string] = signature

        return len(signatures)

    def find_signatures1(self, word_counts, min_stem_len=MIN_STEM_LEN,
                         min_num_stems=MIN_NUM_STEMS, affix_side="suffix"):
        """Find initial signatures (using Goldsmith's Lxa-Crab algorithm).

        Args:
            word_counts (Counter): word to count dictionary
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

        # Store word counts as attribute.
        self.word_counts = word_counts

        # Select affix side...
        signatures = self.get_signatures(affix_side)
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
            for prefix_len in range(MIN_STEM_LEN, len(word)+1):
                prefix = word[:prefix_len]
                if prefix in protostems:
                    continuations[prefix].append(word[prefix_len:])

        # Find all stems associated with each continuation list...
        protostem_lists = collections.defaultdict(set)
        for protostem, continuation in continuations.items():
            protostem_lists[tuple(sorted(continuation))].add(protostem)

        # For each continuation lists with min_num_stems stems or more...
        for continuations, protostems in protostem_lists.items():
            if len(protostems) >= min_num_stems:

                # If affix side is prefix, reverse stems and continuations...
                if affix_side == "prefix":
                    protostems = [protostem[::-1] for protostem in protostems]
                    continuations = [cont[::-1] for cont in continuations]

                # Replace empty affix with NULL_AFFIX.
                continuations = [cont if len(cont) else NULL_AFFIX
                                 for cont in continuations]

                # Get stem and continuation counts...
                protostem_counts = collections.Counter()
                continuation_counts = collections.Counter()
                for protostem in protostems:
                    for continuation in continuations:
                        word_count = word_counts[protostem + continuation]
                        protostem_counts[protostem] += word_count
                        continuation_counts[continuation] += word_count

                # Create and store signature.
                self.add_signature(stems=protostem_counts,
                                   affixes=continuation_counts,
                                   affix_side=affix_side)

    def create_families(self, affix_side="suffix"):
        """Create families; each family has a nucleus signature, which comes
           from the most robust signatures, and it finds other signatures which
           are supersets of the nucleus.

        Args:
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        Todo: test.

        """
        pass

    def learn_from_wordlist(self, wordlist, lowercase_input=LOWERCASE_INPUT,
                            min_stem_len=MIN_STEM_LEN,
                            min_num_stems=MIN_NUM_STEMS, affix_side="suffix"):
        """Learn morphology based on wordlist.

        Args:
            wordlist (list of strings): list of words, possibly repeated
            lowercase_input (bool, optional): indicates whether input words
                should be lowercased (default is LOWERCASE_INPUT).
            min_stem_len (int, optional): minimum number of letters required in
                a stem (default is MIN_STEM_LEN).
            min_num_stems (int, optional): minimum number of stems required in
                a signature (default is MIN_NUM_STEMS).
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        # Lowercase words if needed...
        if lowercase_input:
            wordlist = [word.lower() for word in wordlist]

        # Count words.
        word_counts = collections.Counter(wordlist)

        # Find signatures based on words (stored in word_counts).
        self.find_signatures1(word_counts, min_stem_len, min_num_stems,
                              affix_side)

    def learn_from_string(self, input_string,
                          tokenization_regex=TOKENIZATION_REGEX,
                          lowercase_input=LOWERCASE_INPUT,
                          min_stem_len=MIN_STEM_LEN,
                          min_num_stems=MIN_NUM_STEMS, affix_side="suffix"):
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
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        # Split content into words...
        words = re.findall(tokenization_regex, input_string)

        self.learn_from_wordlist(words, lowercase_input, min_stem_len,
                                 min_num_stems, affix_side)

    def learn_from_file(self, input_file_path, encoding=INPUT_ENCODING,
                        tokenization_regex=TOKENIZATION_REGEX,
                        lowercase_input=LOWERCASE_INPUT,
                        min_stem_len=MIN_STEM_LEN, min_num_stems=MIN_NUM_STEMS,
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
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        Returns: nothing.

        """

        # Attempt to open and read file...
        try:
            input_file = open(input_file_path, encoding=encoding, mode="r")
            content = input_file.read()
            input_file.close()
            self.learn_from_string(content, tokenization_regex,
                                   lowercase_input, min_stem_len,
                                   min_num_stems, affix_side)
        except IOError:
            print("Couldn't read file ", input_file_path)

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

        return AFFIX_DELIMITER.join(str(affix)
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


class Family(object):
    """A class for implementing a family of signature in pycrab.

    A family is a set of signatures related to a single nucleus signature. All
    signatures in a family contain the nucleus, i.e. they are supersets of the
    nucleus. Affixes contained in the superset signatures but not in the
    nucleus are called satellite affixes.

    Examples:
        TODO

    """

    def __init__(self):
        """__init__ method for class Family.

        Args:
            TODO

        """
        pass


