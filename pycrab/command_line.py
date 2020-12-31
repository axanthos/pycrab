#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""File command_line.py

This module provides functionality for command-line usage of pycrab.

"""

import argparse
import configparser
import errno
from pathlib import Path
import sys

import pycrab
import pycrab.graphics

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
        "-a", "--num_seed_families",
        help="The number of seed families to create "
             "(default: %i)" % pycrab.morphology.NUM_SEED_FAMILIES,
        default=pycrab.morphology.NUM_SEED_FAMILIES,
        type=int,
    )
    parser.add_argument(
        "-c", "--case_sensitive",
        help="Take case differences into account "
             "(rather than lowercasing input text)",
        action="store_true"
    )
    parser.add_argument(
        "-e", "--encoding",
        help="Input file encoding (default: %s)" %
             pycrab.morphology.INPUT_ENCODING,
        default=pycrab.morphology.INPUT_ENCODING,
    )
    parser.add_argument(
        "-f", "--config_file",
        help="Path to a .ini file containing configuration instructions",
    )
    parser.add_argument(
        "-i", "--input",
        help="Path to the text file containing the data to analyze",
        default=None,
    )
    parser.add_argument(
        "-n", "--min_num_stems",
        help="The minimum number of stems for creating a signature "
             "(default: %i)" % pycrab.morphology.MIN_NUM_STEMS,
        default=pycrab.morphology.MIN_NUM_STEMS,
        type=int,
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to the folder where output files will be created "
             "(default: print to screen)",
    )
    parser.add_argument(
        "-p", "--prefix",
        help="Learn prefixal (instead of suffixal) morphology",
        action="store_true",
    )
    parser.add_argument(
        "-r", "--min_robustness",
        help="minimal robustness required for a signature to be considered "
             "for inclusion in a family (default: %i)" %
             pycrab.morphology.MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
        default=pycrab.morphology.MIN_ROBUSTNESS_FOR_FAMILY_INCLUSION,
        type=int,
    )
    parser.add_argument(
        "-s", "--min_stem_length",
        help="The minimum number of characters in a stem (default: %i)" %
             pycrab.morphology.MIN_STEM_LEN,
        default=pycrab.morphology.MIN_STEM_LEN,
        type=int,
    )
    parser.add_argument(
        "-t", "--token",
        help="A regular expression to be used for tokenizing input data "
             "(default: '%s')" % pycrab.morphology.TOKENIZATION_REGEX,
        default=pycrab.morphology.TOKENIZATION_REGEX,
    )
    parser.add_argument(
        "-w", "--overwrite",
        help="Overwrite contents of existing output folder (if any) "
             "without asking",
        action="store_true",
    )

    # Parse args.
    args = parser.parse_args()
    
    # If a config file has been provided, read it to get args that are not
    # specified in the command line (command line args have priority)...
    if args.config_file:
        config_file_path = Path(args.config_file)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        for key in config["PYCRAB_CONFIG"]:  
            if not getattr(args, key):
                setattr(args, key, config["PYCRAB_CONFIG"][key])
                
    # Exit with error message if no input file was specified...
    if not args.input:
        parser.print_usage()
        print("pycrab: error: an input file must be specified either in the "
              "command line args (-i/--input) or in a config file (input)")
        exit()
        
    # Process args...
    affix_side = "prefix" if args.prefix else "suffix"
    morphology = pycrab.Morphology()
    try:
        morphology.learn_from_file(
            input_file_path=args.input,
            encoding=args.encoding,
            tokenization_regex=args.token,
            lowercase_input=not args.case_sensitive,
            min_stem_len=args.min_stem_length,
            min_num_stems=args.min_num_stems,
            num_seed_families=args.num_seed_families,
            min_robustness=args.min_robustness,
            affix_side=affix_side,
        )

        text_results = {
            "morphology_overview": morphology.serialize(affix_side),
            "families": morphology.serialize_families(affix_side),
            "signatures_robustness": morphology.serialize_signatures(affix_side),
            "signatures_ascii": morphology.serialize_signatures(affix_side,
                                                                "ascii"),
            "stems_and_words": morphology.serialize_stems_and_words(affix_side),
            "protostems": morphology.serialize_protostems(affix_side),
            "word_biographies": morphology.serialize_word_biographies(affix_side),
            "scratchpad": morphology.serialize_scratchpads()
        }
        
        html_results = {
            "svg-graphics": morphology.produce_svg(affix_side),
        }
        latex_results = {
            "signatures_latex": morphology.signatures_to_latex(affix_side),
        }
        extension_to_result_dict = {
            "txt": text_results,
            "html": html_results,
            "tex": latex_results
        }

        if args.output:
            output_path = Path(args.output)
            try:
                output_path.mkdir()
            except OSError as e:
                if e.errno == errno.EEXIST:
                    if not args.overwrite:
                        overwrite = None
                        while overwrite != "y" and overwrite != "n":
                            overwrite = input("Overwrite contents of "
                                              "existing '%s' folder? [y/n]: " % output_path)
                        if overwrite == "n":
                            print("Operation canceled.")
                            exit()
                else:
                    raise

        for extension, result_dict in extension_to_result_dict.items():
            for filename, result in result_dict.items():
                print_to_screen = False
                if args.output:
                    try:
                        path = output_path / Path("%s.%s" % (filename, 
                                                             extension))
                        with open(path, 'w') as output_file:
                            output_file.write(result)
                    except IOError:
                        print("Couldn't open file %s." % path)
                        print_to_screen = True
                else:
                    print_to_screen = True
                if print_to_screen and extension == "txt":
                    print("printing results to screen.")
                    print("#" * 80 + "\n")
                    print(result)

    except IOError:
        print("Couldn't open file", args.input)


if __name__ == "__main__":
    main()
