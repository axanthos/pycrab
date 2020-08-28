#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File test_signature.py

This module provides unit tests for class Signature in pycrab.

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
        self.signature = morphology.Signature(
            stems=["want", "add", "add"],
            affixes=[morphology.NULL_AFFIX, "ed", "ing"],
        )

    def test_default_affix_side_is_suffix(self):
        self.assertEqual(self.signature.affix_side, "suffix")

    def test_compute_robustness(self):
        self.assertEqual(self.signature.robustness, 19)

    def test_get_edge_entropy(self):
        self.assertEqual(self.signature.get_edge_entropy(), 1.0)

    def test_get_edge_entropy_several_letters(self):
        signature = morphology.Signature(stems=["prey", "pray"])
        self.assertEqual(signature.get_edge_entropy(num_letters=3), 1.0)

    def test_get_edge_entropy_raises_value_error(self):
        self.assertRaises(ValueError, self.signature.get_edge_entropy, 5)

    def test_init_stems_with_lists(self):
        self.assertEqual(self.signature.stems, {"want": 1, "add": 2})

    def test_init_affixes_with_lists(self):
        self.assertEqual(self.signature.affixes,
                         {morphology.NULL_AFFIX: 1, "ed": 1, "ing": 1})

    def test_signature_equality(self):
        other_signature = morphology.Signature(
            stems=["add", "add", "want"],   # Doesn't depend on order.
            affixes=[morphology.NULL_AFFIX, "ed", "ing"],
        )
        self.assertTrue(self.signature == other_signature)

    def test_signature_inequality(self):
        other_signature = morphology.Signature(
            stems=["want", "add"],  # One less "add".
            affixes=[morphology.NULL_AFFIX, "ed", "ing"],
        )
        self.assertTrue(self.signature != other_signature)

    def test_suffixal_parses(self):
        expected_parses = {
            ("want", morphology.NULL_AFFIX),
            ("want", "ed"),
            ("want", "ing"),
            ("add", morphology.NULL_AFFIX),
            ("add", "ed"),
            ("add", "ing"),
        }
        self.assertEqual(self.signature.parses, expected_parses)

    def test_prefixal_parses(self):
        signature = morphology.Signature(
            stems=["do", "wind"],
            affixes=["un", "re"],
            affix_side="prefix",
        )
        expected_parses = {
            ("un", "do"),
            ("re", "do"),
            ("un", "wind"),
            ("re", "wind"),
        }
        self.assertEqual(signature.parses, expected_parses)

    def test_affix_string(self):
        self.assertEqual(self.signature.affix_string, "NULL=ed=ing")

    def test_example_stem(self):
        self.assertEqual(self.signature.example_stem, "add")

    def test_str(self):
        signature = morphology.Signature(["want", "want", "add"],
                                         ["ing", "ed", morphology.NULL_AFFIX])
        expected_str = (
            "================================================== NULL=ed=ing\n"
            "\n"
            "add     want\n"
            "------------------------\n"
            "want 2     add  1    \n"
            "------------------------\n"
            "\n"
            "    Letters in words if unanalyzed:         31\n"
            "               Letters as analyzed:         12\n"
            "\n"
            "Final stem letter entropy: 1.000\n"
            "\n"
            "Number of stems: 2\n"
        )
        self.assertEqual(str(signature), expected_str)
