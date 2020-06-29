# -*- coding: utf-8 -*-
"""File test_morphology.py

This module provides unit tests for classes Morphology, Signature, and 
NULLAffix in pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from six import string_types

from unittest import TestCase

from pycrab import morphology


class TestNULLAffix(TestCase):

    def test_NULLAffix_is_string(self):
        suffix = morphology.NULLAffix()
        self.assertTrue(isinstance(suffix, string_types))