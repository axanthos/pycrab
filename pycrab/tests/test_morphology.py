#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File test_morphology.py

This module provides unit tests for class Morphology in pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from unittest import TestCase

from pycrab import morphology

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class TestSignature(TestCase):

    def setUp(self):
        self.morphology = morphology.Morphology(
            suffixal_signatures=[
                morphology.Signature(
                    stems=["want", "add", "add"],
                    affixes=[morphology.NULL_AFFIX, "ed", "ing"],
                ),
                morphology.Signature(
                    stems=["cr", "dr"],
                    affixes=["y", "ied"],
                ),
            ],
            prefixal_signatures=[
                morphology.Signature(
                    stems=["do", "wind"],
                    affixes=["un", "re"],
                    affix_side="prefix",
                ),
                morphology.Signature(
                    stems=["make", "create"],
                    affixes=["re", morphology.NULL_AFFIX],
                    affix_side="prefix",
                ),
            ],
        )

    def test_morphology_equality(self):
        other_morphology = morphology.Morphology(
            suffixal_signatures=[
                morphology.Signature(   # NB equality doesn't depend on order.
                    stems=["cr", "dr"],
                    affixes=["y", "ied"],
                ),
                morphology.Signature(
                    stems=["want", "add", "add"],
                    affixes=[morphology.NULL_AFFIX, "ed", "ing"],
                ),
            ],
            prefixal_signatures=[
                morphology.Signature(
                    stems=["do", "wind"],
                    affixes=["un", "re"],
                    affix_side="prefix",
                ),
                morphology.Signature(
                    stems=["make", "create"],
                    affixes=["re", morphology.NULL_AFFIX],
                    affix_side="prefix",
                ),
            ],
        )
        self.assertTrue(self.morphology == other_morphology)

    def test_morphology_inequality(self):
        other_morphology = morphology.Morphology(
            suffixal_signatures=[
                morphology.Signature(
                    stems=["want", "add"],  # One less "add".
                    affixes=[morphology.NULL_AFFIX, "ed", "ing"],
                ),
                morphology.Signature(
                    stems=["cr", "dr"],
                    affixes=["y", "ied"],
                ),
            ],
            prefixal_signatures=[
                morphology.Signature(
                    stems=["do", "wind"],
                    affixes=["un", "re"],
                    affix_side="prefix",
                ),
                morphology.Signature(
                    stems=["make", "create"],
                    affixes=["re", morphology.NULL_AFFIX],
                    affix_side="prefix",
                ),
            ],
        )
        self.assertTrue(self.morphology != other_morphology)

    def test_stems(self):
        expected_stems = {"want", "add", "dr", "cr",
                          "create", "wind", "make", "do"}
        self.assertEqual(self.morphology.stems, expected_stems)

    def test_suffixes(self):
        expected_suffixes = {morphology.NULL_AFFIX, "ed", "ing", "y", "ied"}
        self.assertEqual(self.morphology.suffixes, expected_suffixes)

    def test_prefixes(self):
        expected_prefixes = {morphology.NULL_AFFIX, "un", "re"}
        self.assertEqual(self.morphology.prefixes, expected_prefixes)

    def test_suffixal_parses(self):
        expected_parses = {
            ("want", morphology.NULL_AFFIX),
            ("want", "ed"),
            ("want", "ing"),
            ("add", morphology.NULL_AFFIX),
            ("add", "ed"),
            ("add", "ing"),
            ("dr", "y"),
            ("dr", "ied"),
            ("cr", "y"),
            ("cr", "ied"),
        }
        self.assertEqual(self.morphology.suffixal_parses, expected_parses)

    def test_prefixal_parses(self):
        expected_parses = {
            ("un", "do"),
            ("re", "do"),
            ("un", "wind"),
            ("re", "wind"),
            (morphology.NULL_AFFIX, "make"),
            ("re", "make"),
            (morphology.NULL_AFFIX, "create"),
            ("re", "create"),
        }
        self.assertEqual(self.morphology.prefixal_parses, expected_parses)

    def test_build_suffixal_signatures(self):
        existing_morphology = morphology.Morphology()
        parses = {
            ("want", morphology.NULL_AFFIX),
            ("want", "ed"),
            ("want", "ing"),
            ("add", morphology.NULL_AFFIX),
            ("add", "ed"),
            ("add", "ing"),
            ("dr", "y"),
            ("dr", "ied"),
            ("cr", "y"),
            ("cr", "ied"),
            ("boot", morphology.NULL_AFFIX),    # 'boot' should not be retained
            ("boot", "s")                       # because min_num_stems=2
        }
        expected_morphology = morphology.Morphology(
            suffixal_signatures=[
                morphology.Signature(
                    stems=["want", "add"],
                    affixes=[morphology.NULL_AFFIX, "ed", "ing"],
                ),
                morphology.Signature(
                    stems=["cr", "dr"],
                    affixes=["y", "ied"],
                ),
            ],
        )
        existing_morphology.build_signatures(parses, min_num_stems=2)
        self.assertTrue(existing_morphology == expected_morphology)

    def test_build_prefixal_signatures(self):
        existing_morphology = morphology.Morphology()
        parses = {
            ("un", "do"),
            ("re", "do"),
            ("un", "wind"),
            ("re", "wind"),
            (morphology.NULL_AFFIX, "make"),
            ("re", "make"),
            (morphology.NULL_AFFIX, "create"),
            ("re", "create"),
            ("dis", "able"),    # 'able' should be retained (min_num_stems=1)
        }
        expected_morphology = morphology.Morphology(
            prefixal_signatures=[
                morphology.Signature(
                    stems=["do", "wind"],
                    affixes=["un", "re"],
                    affix_side="prefix",
                ),
                morphology.Signature(
                    stems=["make", "create"],
                    affixes=["re", morphology.NULL_AFFIX],
                    affix_side="prefix",
                ),
                morphology.Signature(
                    stems=["able"],
                    affixes=["dis"],
                    affix_side="prefix",
                ),
            ],
        )
        existing_morphology.build_signatures(parses, affix_side="prefix",
                                             min_num_stems=1)
        self.assertTrue(existing_morphology == expected_morphology)
