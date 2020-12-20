#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File test_null_affix.py

This module provides unit tests for utils module in pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
from unittest import TestCase

from pycrab import Morphology
from pycrab import Signature
from pycrab import utils

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class TestUTils(TestCase):

    def test_entropy(self):
        self.assertEqual(utils.entropy({"a": 1, "b": 1, "c": 0}), 1.0)

    def test_format_if_shadow(self):
        self.assertEqual(utils.format_if_shadow("test", ["test"]), "[test]")

    def test_format_if_not_shadow(self):
        self.assertEqual(utils.format_if_shadow("test", []), "test")
