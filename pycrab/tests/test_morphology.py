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
        suffixal_sig = morphology.Signature(
            stems=["want", "add", "add"],
            affixes=[morphology.NULLAffix(), "ed", "ing"],
        )
        suffixal_sig2 = morphology.Signature(
            stems=["cr", "dr"],
            affixes=["y", "ied"],
        )
        prefixal_sig = morphology.Signature(
            stems=["do", "wind"],
            affixes=["un", "re"],
            affix_side="prefix",
        )
        prefixal_sig2 = morphology.Signature(
            stems=["make", "create"],
            affixes=["re", morphology.NULLAffix()],
            affix_side="prefix",
        )
        self.morphology = morphology.Morphology(
            signatures={
                suffixal_sig,
                suffixal_sig2,
                prefixal_sig,
                prefixal_sig2,
            },
            # AX => JG: shouldn't what follows be computed based on signatures,
            # rather?
            stems={
                "want": suffixal_sig,
                "add": suffixal_sig,
                "cr": suffixal_sig2,
                "dr": suffixal_sig2,
                "do": prefixal_sig,
                "wind": prefixal_sig,
                "make": prefixal_sig2,
                "create": prefixal_sig2,
            },
            suffixes={
                morphology.NULLAffix(),
                "ed",
                "ing",
            },
            prefixes={
                "re",
                "un",
            },
        )

    def test_suffixal_parses(self):
        expected_parses = {
            ("want", morphology.NULLAffix()),
            ("want", "ed"),
            ("want", "ing"),
            ("add", morphology.NULLAffix()),
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
            (morphology.NULLAffix(), "make"),
            ("re", "make"),
            (morphology.NULLAffix(), "create"),
            ("re", "create"),
        }
        self.assertEqual(self.morphology.prefixal_parses, expected_parses)

