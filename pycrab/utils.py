#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File utils.py

This module provides utility functions for pycrab.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math

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
    return (math.log(my_sum) - weighted_sum_of_logs / my_sum) / math.log(2)
