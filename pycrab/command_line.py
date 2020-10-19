#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File command_line.py

This module provides functionality for command-line usage of pycrab.

"""

import argparse
from pathlib import Path
import sys

import pycrab

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
        action="store_true" if pycrab.morphology.LOWERCASE_INPUT
                            else "store_false"
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
        help="Input file encoding (default: %s)" %
             pycrab.morphology.INPUT_ENCODING,
        default=pycrab.morphology.INPUT_ENCODING,
    )
    parser.add_argument(
        "-o", "--output",
        help="Base filename (without suffix) for output files "
             "(default: print to screen)",
    )
    parser.add_argument(
        "-t", "--token",
        help="A regular expression to be used for tokenizing input data "
             "(default: '%s')" % pycrab.morphology.TOKENIZATION_REGEX,
        default=pycrab.morphology.TOKENIZATION_REGEX,
    )
    parser.add_argument(
        "-s", "--min_stem_length",
        help="The minimum number of characters in a stem (default: %i)" %
             pycrab.morphology.MIN_STEM_LEN,
        default=pycrab.morphology.MIN_STEM_LEN,
        type=int,
    )
    parser.add_argument(
        "-n", "--min_num_stems",
        help="The minimum number of stems for creating a signature "
             "(default: %i)" % pycrab.morphology.MIN_NUM_STEMS,
        default=pycrab.morphology.MIN_NUM_STEMS,
        type=int,
    )
    parser.add_argument(
        "-f", "--num_seed_families",
        help="The number of seed families to create "
             "(default: %i)" % pycrab.morphology.NUM_SEED_FAMILIES,
        default=pycrab.morphology.NUM_SEED_FAMILIES,
        type=int,
    )
    parser.add_argument(
        "-r", "--min_robustness",
        help="minimal robustness required for a signature to be considered "
             "for inclusion in a family (default: %i)" %
             pycrab.morphology.MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
        default=pycrab.morphology.MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
        type=int,
    )

    # Parse and process args.
    args = parser.parse_args()
    affix_side = "prefix" if args.prefix else "suffix"
    morphology = pycrab.Morphology()
    try:
        morphology.learn_from_file(
            input_file_path=args.input,
            encoding=args.encoding,
            tokenization_regex=args.token,
            lowercase_input=args.lowercase,
            min_stem_len=args.min_stem_length,
            min_num_stems=args.min_num_stems,
            num_seed_families=args.num_seed_families,
            min_robustness=args.min_robustness,
            affix_side=affix_side,
        )

        results = {
            "morphology_overview": morphology.serialize(affix_side),
            "families": morphology.serialize_families(affix_side),
            "signatures_robustness": morphology.serialize_signatures(affix_side),
            "signatures_ascii": morphology.serialize_signatures(affix_side,
                                                                "ascii"),
            "stems_and_words": morphology.serialize_stems_and_words(affix_side),
            "protostems": morphology.serialize_protostems(affix_side),
            "word_biographies": morphology.serialize_word_biographies(affix_side),
        }

        if args.output:
            base_path = Path(args.input).parent / args.output
        for filename, result in results.items():
            if args.output:
                try:
                    path = "%s_%s.txt" % (base_path, filename)
                    sys.stdout = open(path, 'w')
                except IOError:
                    print("Couldn't open file %s, printing results to screen." %
                          args.output)
            if not sys.stdout.name.endswith(".txt"):
                print("#" * 80 + "\n")
            print(result)
        sys.stdout = sys.__stdout__

    except IOError:
        print("Couldn't open file", args.input)


if __name__ == "__main__":
    main()