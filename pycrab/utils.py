#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File utils.py

This module provides utility functions for pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import functools
import math

from pycrab import morphology


__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"


def entropy(counts):
    """Compute the entropy (in bits) of a dictionary storing counts.

        Args:
            counts (dict): a dictionary storing counts (e.g. an instance of
                collections.Counter).

        Returns:
            float.

    """

    my_sum = 0
    weighted_sum_of_logs = 0
    for count in counts.values():
        if count:
            my_sum += count
            weighted_sum_of_logs += count * math.log(count)
    return abs((math.log(my_sum) - weighted_sum_of_logs/my_sum) / math.log(2))


def format_if_shadow(affix_string, shadow_signatures):
    """Applies standard formatting to an affix string if is in a list of shadow
       signatures.

        Args:
            affix_string (string): the affix string of a signature.
            shadow_signatures (set): a set of (affix strings) of shadow
                signatures.

        Returns:
            string.

    """

    if affix_string in shadow_signatures:
        return "[%s]" % affix_string
    else:
        return affix_string


def strip_index(affix, affix_side="suffix"):
    """Returns a name without index for an affix.

    Args:
        affix (string): the affix from which the index should be removed.
        affix_side (string, optional): either "suffix" (default) or "prefix".

    Returns:
        string.

    Todo: test.

    """

    if affix == morphology.NULL_AFFIX:
        return affix

    location = affix.find(morphology.AFFIX_MARKER)
    if location == -1:
        return affix
    else:
        if affix_side == "prefix":
            return affix[location+1:]
        else:
            return affix[:location]


class ImmutableDict(dict):
    """Immutable dict, based on https://gist.github.com/glyphobet/2687745.

    Todo: unit tests.

    """

    def __init__(self, arg):
        # Initialize dict like collections.Counter.
        super(ImmutableDict, self).__init__(collections.Counter(arg))

    def __setitem__(self, key, value):
        raise TypeError("%r object does not support item assignment"
                        % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion"
                        % type(self).__name__)

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError("%r object has no attribute %r"
                                 % (type(self).__name__, attribute))
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def fromkeys(self, S, v):
        return type(self)(dict(self).fromkeys(S, v))
