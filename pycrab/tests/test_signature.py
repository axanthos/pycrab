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

__author__ = "Aris Xanthos"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris dot xanthos at unil dot ch"
__status__ = "development"


class TestSignature(TestCase):

    def setUp(self):
        self.signature = morphology.Signature(
            stems=["want", "add", "add"],
            affixes=[morphology.NULLAffix(), "ed", "ing"],
        )

    def test_default_affix_side_is_suffix(self):
        self.assertEqual(self.signature.affix_side, "suffix")
        
    def test_compute_robustness(self):
        self.assertEqual(self.signature.robustness, 19)

