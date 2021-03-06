#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File test_null_affix.py

This module provides unit tests for class NULLAffix in pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from unittest import TestCase

from six import string_types

from pycrab import null_affix

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class TestNULLAffix(TestCase):

    def setUp(self):
        self.suffix = null_affix.NULLAffix()

    def test_is_string(self):
        self.assertTrue(isinstance(self.suffix, string_types))

    def test_is_singleton(self):
        self.assertTrue(self.suffix is null_affix.NULLAffix())

    def test_has_zero_length(self):
        self.assertEqual(len(self.suffix), 0)

    def test_is_empty_when_concatenated(self):
        self.assertEqual("" + self.suffix, "")

    def test_is_visible_when_passed_to_str(self):
        self.assertEqual(str(self.suffix), "NULL")

    def test_raises_exception_when_init_with_arg(self):
        self.assertRaises(TypeError, null_affix.NULLAffix, "")
