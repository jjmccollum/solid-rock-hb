#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_usfm_converter import tei_usfm_converter

"""
Dictionary mapping witness references to sigla.
"""
wit_sigla = {
    "#SR": "SR",
    "#WLC": "L"
}

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description="Converts a labeled TEI XML collation to a USFM file.")
    parser.add_argument("-a", metavar="ignored_app_type", type=str, action="append", help="Variation type to ignore; this can used multiple times (e.g., -a vocalic -a orthographic).")
    parser.add_argument("-o", metavar="output", type=str, help="Output file address (the default will use the input file base with the .sfm extension).")
    parser.add_argument("input", type=str, help="TEI XML collation file to convert to USFM.")
    args = parser.parse_args()
    # Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace(".xml", ".sfm")
    ignored_app_types = set() if args.a is None else set(args.a)
    # Create the parameters for the converter:
    converter_args = {}
    converter_args["wit_sigla"] = wit_sigla
    converter_args["ignored_app_types"] = ignored_app_types
    # Initialize the converter with these parameters:
    converter = tei_usfm_converter(**converter_args)
    # Parse the input XML document:
    input_xml = et.parse(input_addr)
    # Convert the input and write to output:
    usfm = converter.to_usfm(input_xml)
    with open(output_addr, "w", encoding="utf-8") as f:
        f.write(usfm)
        f.close()
    exit(0)

if __name__=="__main__":
    main()
