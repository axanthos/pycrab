#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File __init__.py

This module exports some basic classes so they can be more conveniently
imported by pycrab client code.

Examples:
    >>> import pycrab
    >>> pycrab.Morphology()
    <pycrab.morphology.Morphology object at 0x000002AB743176A0>
    >>> pycrab.Signature()
    <pycrab.morphology.Signature object at 0x000002AB74317E80>
    >>> pycrab.NULL_AFFIX
    NULL

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

from pycrab.morphology import Morphology, Signature, NULL_AFFIX
