#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File command_line.py

This module provides functionality for command-line usage of pycrab.

"""

import argparse
import sys

from pycrab import Morphology

__author__ = "Aris Xanthos and John Goldsmith"
__copyright__ = "Copyright 2020, Aris Xanthos & John Golsdmith"
__credits__ = ["John Goldsmith", "Aris Xanthos"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"
__status__ = "development"

def main():
    """Command line usage of pycrab"""
    
    # Create argument parser and declare arguments...
    parser = argparse.ArgumentParser(
        prog="pycrab",
        description="Unsupervised morphological analysis with the Linguistica "
                    "Crab algorithm.",
    )
    parser.add_argument(
        "-l", "--lowercase",
        help="Lowercase input text",
        action="store_true",
    )
    parser.add_argument(
        "-p", "--prefix",
        help="Learn prefixal (instead of suffixal) morphology",
        action="store_true",
    )
    parser.add_argument(
        "-i", "--input",
        help="Path to the text file containing the data to analyze",
        required=True,
    )
    parser.add_argument(
        "-e", "--encoding",
        help="Input file encoding (default: utf8)",
        default="utf8",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to a file where results will be saved "
             "(default: print to screen)",
    )
    parser.add_argument(
        "-r", "--regex",
        help="A regular expression to be used for tokenizing input data "
             "(default: '\w+(?u)')",
        default=r"\w+(?u)",
    )
    parser.add_argument(
        "-s", "--min_stem_length",
        help="The minimum number of characters in a stem (default: 4)",
        default=4,
        type=int,
    )
    parser.add_argument(
        "-n", "--min_num_stems",
        help="The minimum number of stems for creating a signature "
             "(default: 2)",
        default=2,
        type=int,
    )

    # Parse and process args.
    args = parser.parse_args()
    affix_side = "prefix" if args.prefix else "suffix"
    morphology = Morphology()
    morphology.learn_from_file(
        input_file_path=args.input, 
        encoding=args.encoding,
        tokenization_regex=args.regex,
        lowercase_input=args.lowercase,
        min_stem_len=args.min_stem_length, 
        min_num_stems=args.min_num_stems,
        affix_side=affix_side,
    )

    if args.output:
        try:
            sys.stdout = open(args.output, 'w')
        except IOError:
            print("Couldn't open file %s, printing results to screen." % 
                  args.output)

    print(morphology.serialize(affix_side), "\n")
    print(morphology.serialize_signatures(affix_side))
    sys.stdout = sys.__stdout__
    
    
if __name__ == "__main__":
    main()