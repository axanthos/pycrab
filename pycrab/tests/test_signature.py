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

    def test_init_stems_with_lists(self):
        self.assertEqual(self.signature.stems, {"want": 1, "add": 2})

    def test_init_affixes_with_lists(self):
        self.assertEqual(self.signature.affixes,
                         {morphology.NULL_AFFIX: 1, "ed": 1, "ing": 1})

    def test_init_stem_increment(self):
        signature = morphology.Signature(
            stems=["want", "add", "add"],
            affixes=[morphology.NULL_AFFIX, "ed", "ing"],
        )
        signature.stems["test"] += 1
        self.assertEqual(signature.stems["test"], 1)

    def test_init_affix_increment(self):
        signature = morphology.Signature(
            stems=["want", "add", "add"],
            affixes=[morphology.NULL_AFFIX, "ed", "ing"],
        )
        signature.affixes["s"] += 1
        self.assertEqual(signature.affixes["s"], 1)

    def test_signature_equality(self):
        other_signature = morphology.Signature(
            stems=["want", "add", "add"],
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
