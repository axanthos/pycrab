#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File null_affix.py

This module provides class NULLAffix, which is used to represent the NULL
affix in a description of the morphology of a language in pycrab. The
implementation relies on the singleton pattern. Note that the NULLAffix class
is not meant to be directly instantiated by client code. Rather, it is
instantiated as a module-level constant in the morphology.py module and meant
to be referred to via this constant (morphology.NULL_AFFIX).

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


class NULLAffix(str):
    """A class for representing the NULL affix in pycrab.

    The NULL affix behaves like an empty string in most situations, such as
    when being concatenated with stems or when its length is computed, however
    it can be represented by a predefined string ("NULL") when necessary,
    by calling print, str, or repr on it.

    Implementation uses the singleton pattern presented in
    https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    (contributed by Dmitry Balabanov)

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

    __instance = None

    def __new__(cls):
        if NULLAffix.__instance is None:
            NULLAffix.__instance = str.__new__(cls)
        return NULLAffix.__instance

    def __str__(self):
        return "NULL"

    def __repr__(self):
        return self.__str__()
