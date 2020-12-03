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

    # def test_biograph_decorator(self):

        # class DummyClassForTestingBiographDecorator():
            # def __init__(self, bigrams):
                # self.word_biographies = collections.defaultdict(dict)
                # self.bigrams = bigrams
                # self.word_counts = {"".join(bigram): 1 for bigram in bigrams}
                # self.analyses_list = list()
            # def get_bigrams(self, affix_side="suffix"):
                # return self.bigrams
            # def get_analyses_list(self, affix_side="suffix"):
                # return self.analyses_list
            # def get_word_biographies(self, affix_side="suffix"):
                # return self.word_biographies
            # @utils.biograph
            # def dummy_method(self, affix_side="suffix"):
                # pass
            # @utils.biograph
            # def dummy_method2(self, affix_side="suffix"):
                # pass

        # bigrams = {("want", "ed"), ("want", "ing"), ("add", "ed"),
                  # ("add", "ing")}
        # word_to_bigrams = collections.defaultdict(dict)
        # for bigram in bigrams:
            # word_to_bigrams["".join(bigram)]["dummy_method"] = {bigram}
            # word_to_bigrams["".join(bigram)]["dummy_method2"] = {bigram}
        # dummy_object = DummyClassForTestingBiographDecorator(bigrams)
        # dummy_object.dummy_method()
        # dummy_object.dummy_method2()
        # self.assertEqual(dummy_object.get_word_biographies(), word_to_bigrams)

    def test_format_if_shadow(self):
        self.assertEqual(utils.format_if_shadow("test", ["test"]), "[test]")

    def test_format_if_not_shadow(self):
        self.assertEqual(utils.format_if_shadow("test", []), "test")
