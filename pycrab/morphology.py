# -*- coding: utf-8 -*-
"""File morphology.py

This module provides classes Morphology, Signature, and NULLAffix, which are 
used to describe the morphology of a language in pycrab. The highest-level 
object is the Morphology, which among other attributes has a list of Signature
objects. A NULLAffix can be part of a list of affixes either in the morphology
itself or in individual signatures.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import Counter


class Signature(object):
    """A class for implementing a signature in pycrab.
    
    The Signature class that is at the heart of pycrab's morphology 
    representation and learning procedures. A signature has an "affix side" 
    (either "suffix", the default, or "prefix"), as well as a dict of stems and
    a dict of affixes, each of which has integer counts as values. Stems and 
    affixes can be initialized either with dicts or with other iterables such 
    as lists and sets.

    Examples:
        >>> sig = pycrab.Signature(stems=["add"], affixes={"ing": 8, "ed": 6})
        >>> sig.stems["want"] = 1
        >>> sig.stems["want"] += 1
        >>> sig.stems.update({"play": 2, "guess": 1})
        >>> sig.stems
        {'add': 1, 'want': 2, 'play': 2, 'guess': 1}
        >>> sig.affixes[NULLAffix()] += 6
        >>> sig.affixes
        {'ing': 8, 'ed': 6, NULL: 6}
        >>> sig2  = pycrab.Signature(stems=["want", "want", "add"])
        >>> sig2.stems
        {'want': 2, 'add': 1}

    Todo:
        * Compute robustness
        * Compute stability_entropy
        
    """

    def __init__(self, stems=None, affixes=None, affix_side="suffix"):
        """__init__ method for class Signature.
        
        Args:
            stems (mapping or iterable, optional): stems associated with this 
                signature (with counts if arg is a dict). Defaults to empty 
                dict/list.
            affixes (mapping or iterable, optional): affixes associated with 
                this signature (with counts if arg is a dict). Defaults to 
                empty dict/list.
            affix_side (string, optional): either "suffix" (default) or
                "prefix".

        """
        self.stems = collections.Counter(stems)
        self.affixes = collections.Counter(affixes)
        self.affix_side = affix_side
        
    @property
    def robustness(self):
        """Returns the robustness of the signature.
        
        Robustness is the number of letters saved by a signature, which equals 
        the sum of the lengths of all words covered by the signature, minus the
        sum of the lengths of stems, minus the sum of the lengths of affixes.

        Returns: 
            int.
            
        """
        saved_stem_length = len("".join(self.stems)) * (len(self.affixes)-1)
        saved_affix_length = len("".join(self.affixes)) * (len(self.stems)-1)
        return saved_stem_length + saved_affix_length
        

class NULLAffix(str):
    """A class for representing a NULL affix in pycrab.
    
    NULL affixes behave like empty strings in most situations, such as when
    being concatenated with stems or when their length is computed, however
    they can be represented by a predefined string ("NULL") when necessary,
    by calling the str or repr functions on them.

    Examples:
        >>> suffix = NULLAffix()
        >>> len(suffix)
        0
        >>> print("test" + suffix)
        test
        >>> print("test", suffix)
        test NULL
        >>> str(suffix)
        'NULL'
        
    """
    
    def __init__(self):
        """Initializes an empty string.
        
        This method is here to throw an exception if a NULLAffix is initialized
        with some kind of string (even empty) as argument.
        
        """
        super().__init__()
        
    def __str__(self):
        return("NULL")
        
    def __repr__(self):
        return "'%s'" % self.__str__()
        