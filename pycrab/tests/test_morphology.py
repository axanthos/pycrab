#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File test_morphology.py

This module provides unit tests for class Morphology in pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from unittest import TestCase
from unittest.mock import patch

from collections import Counter
import tempfile
import os

from pycrab import morphology

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class TestMorphology(TestCase):

    def setUp(self):
        self.morphology = morphology.Morphology(
            morphology.Signature(
                stems=["want", "add", "add"],
                affixes=[morphology.NULL_AFFIX, "ed", "ing"],
            ),
            morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            ),
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
        )

    def test_morphology_equality(self):
        other_morphology = morphology.Morphology(
            morphology.Signature(   # NB: equality doesn't depend on order.
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            ),
            morphology.Signature(
                stems=["add", "add", "want"],
                affixes=[morphology.NULL_AFFIX, "ed", "ing"],
            ),
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
        )
        self.assertTrue(self.morphology == other_morphology)

    def test_morphology_inequality(self):
        other_morphology = morphology.Morphology(
            morphology.Signature(
                stems=["want", "add"],  # One less "add".
                affixes=[morphology.NULL_AFFIX, "ed", "ing"],
            ),
            morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            ),
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
        )
        self.assertTrue(self.morphology != other_morphology)
        
    def test_add_prefixal_signature(self):
        signature = morphology.Signature(
                stems=["do", "wind"],
                affixes=["un", "re"],
                affix_side="prefix",
        )
        other_morphology = morphology.Morphology()
        other_morphology.add_signature(signature.stems, signature.affixes, 
                                       affix_side="prefix")
        self.assertTrue(other_morphology.get_signature(signature.affix_string,
                        affix_side="prefix") == signature)
        
    def test_add_suffixal_signature(self):
        signature = morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
        )
        other_morphology = morphology.Morphology()
        other_morphology.add_signature(signature.stems, signature.affixes)
        self.assertTrue(other_morphology.get_signature(signature.affix_string) 
                        == signature)

        
    def test_get_prefixal_signature(self):
        signature = morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
        )
        other_morphology = morphology.Morphology(signature)
        affix_string = "ied=y".replace("=", morphology.AFFIX_DELIMITER)
        self.assertTrue(other_morphology.get_signature(affix_string) 
                        == signature)

    def test_get_suffixal_signature(self):
        signature = morphology.Signature(
            stems=["do", "wind"],
            affixes=["un", "re"],
            affix_side="prefix",
        )
        other_morphology = morphology.Morphology(signature)
        affix_string = "re=un".replace("=", morphology.AFFIX_DELIMITER)
        self.assertTrue(other_morphology.get_signature(affix_string, 
                        affix_side="prefix") == signature)

    def test_get_signature_raises_value_error(self):
        self.assertRaises(ValueError, self.morphology.get_signature, "dummy")

    def test_get_suffixal_signatures(self):
        expected_signatures = [
            morphology.Signature(
                stems=["want", "add", "add"],
                affixes=[morphology.NULL_AFFIX, "ed", "ing"],
            ),
            morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            ),
        ]
        self.assertTrue(self.morphology.get_signatures() 
                        == expected_signatures)

    def test_get_prefixal_signatures(self):
        expected_signatures = [
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
        ]
        self.assertTrue(self.morphology.get_signatures(affix_side="prefix") 
                        == expected_signatures)

    def test_get_shadow_signatures(self):
        my_morphology = morphology.Morphology(
            morphology.Signature(
                stems=["chang"],
                affixes=["e", "ed", "es", "ing"],
            ),
            morphology.Signature(
                stems=["structural"],
                affixes=["ism", "ist"],
            ),
        )
        expected_affix_strings = {s.replace("=", morphology.AFFIX_DELIMITER)
                                  for s in ["NULL=d=s", "m=t"]}
        print(my_morphology.get_shadow_signatures(), expected_affix_strings)
        self.assertTrue(my_morphology.get_shadow_signatures() 
                        == expected_affix_strings)

    def test_suffixal_stems(self):
        expected_stems = {"want", "add", "dr", "cr"}
        self.assertEqual(self.morphology.suffixal_stems, expected_stems)

    def test_prefixal_stems(self):
        expected_stems = {"create", "wind", "make", "do"}
        self.assertEqual(self.morphology.prefixal_stems, expected_stems)

    def test_suffixes(self):
        expected_suffixes = {morphology.NULL_AFFIX, "ed", "ing", "y", "ied"}
        self.assertEqual(self.morphology.suffixes, expected_suffixes)

    def test_prefixes(self):
        expected_prefixes = {morphology.NULL_AFFIX, "un", "re"}
        self.assertEqual(self.morphology.prefixes, expected_prefixes)

    @patch('pycrab.Morphology.find_signatures1')
    def test_learn_from_wordlist_lower(self, mock_find_signatures1):
        my_morphology = morphology.Morphology()
        wordlist = ["Test", "data", "test"]
        wordlist_lower = [word.lower() for word in wordlist]
        my_morphology.learn_from_wordlist(wordlist, True, 1, 1, "prefix")
        mock_find_signatures1.assert_called_with(Counter(wordlist_lower), 1, 1,
                                                 "prefix")

    @patch('pycrab.Morphology.find_signatures1')
    def test_learn_from_wordlist_not_lower(self, mock_find_signatures1):
        my_morphology = morphology.Morphology()
        wordlist = ["Test", "data", "test"]
        my_morphology.learn_from_wordlist(wordlist, False, 1, 1, "prefix")
        mock_find_signatures1.assert_called_with(Counter(wordlist), 1, 1,
                                                 "prefix")

    @patch('pycrab.Morphology.learn_from_wordlist')
    def test_learn_from_string(self, mock_learn_from_wordlist):
        my_morphology = morphology.Morphology()
        my_morphology.learn_from_string("Test data test", r"\w+", False, 1, 1,
                                        "prefix")
        mock_learn_from_wordlist.assert_called_with(["Test", "data", "test"],
                                                    False, 1, 1, "prefix")

    @patch('pycrab.Morphology.learn_from_string')
    def test_learn_from_file(self, mock_learn_from_string):
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(b"Test data test")
        name = temp.name
        temp.close()
        my_morphology = morphology.Morphology()
        my_morphology.learn_from_file(name, "utf8", r"\w+", False, 1, 1,
                                      "prefix")
        mock_learn_from_string.assert_called_with("Test data test", r"\w+",
                                                    False, 1, 1, "prefix")
        os.remove(name)

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
            morphology.Signature(
                stems=["want", "add"],
                affixes=[morphology.NULL_AFFIX, "ed", "ing"],
            ),
            morphology.Signature(
                stems=["cr", "dr"],
                affixes=["y", "ied"],
            ),
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
        )
        existing_morphology.build_signatures(parses, affix_side="prefix",
                                             min_num_stems=1)
        self.assertTrue(existing_morphology == expected_morphology)
