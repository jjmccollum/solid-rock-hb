#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_latex_converter import tei_latex_converter

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Converts a labeled TEI XML collation to a LaTeX script and writes the result to output.')
    parser.add_argument('-s', metavar='subfiles_path', type=str, help='Relative path for subfiles source in output file (e.g., ../main/main.tex)')
    parser.add_argument('-a', metavar='ignored_app_type', type=str, action='append', help='Variation type to ignore; this can used multiple times (e.g., -a vocalic -a orthographic)')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (the default will use the input file base with the .tex extension).')
    parser.add_argument('input', type=str, help='TEI XML collation file to convert to LaTeX.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace('.xml', '.tex')
    #Create the parameters for the converter:
    converter_args = {}
    if args.s is not None:
        converter_args['subfiles_path'] = args.s
    ignored_app_types = set() if args.a is None else set(args.a)
    converter_args['ignored_app_types'] = ignored_app_types
    #Use hardcoded witness substitution patterns:
    wit_sub_patterns = [
        ('#SRO', 'SRO'), #remove reference marker to get siglum
        #('#WLC-ketiv #WLC-qere', 'L'), #consolidate ketiv and qere when they agree on a reading and convert to siglum
        #('#WLC-ketiv', 'L\\textsuperscript{k}'), #convert reference to siglum with LaTeX formatting
        #('#WLC-qere', 'L\\textsuperscript{q}')  #convert reference to siglum with LaTeX formatting
        ('#WLC', 'L') #convert reference to siglum
    ]
    converter_args['wit_sub_patterns'] = wit_sub_patterns
    #Initialize the converter with these parameters:
    converter = tei_latex_converter(**converter_args)
    #Parse the input XML document:
    input_xml = et.parse(input_addr)
    #Convert the input and write to output:
    latex = converter.to_latex(input_xml)
    #Then write it to the output address:
    output_latex = open(output_addr, 'w', encoding='utf-8')
    output_latex.write(latex)
    output_latex.close()
    exit(0)

if __name__=="__main__":
    main()
