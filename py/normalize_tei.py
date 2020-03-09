#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_normalizer import tei_normalizer

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Normalizes a TEI XML transcription and outputs the result as a TEI XML file.')
    parser.add_argument('-a', metavar='accent_type', type=str, action='append', choices=['cantillation', 'pointing', 'extraordinaire'], help='Names of accentuation sets to strip; this can be used multiple times (e.g., -a cantillation -a extraordinaire)')
    parser.add_argument('-p', metavar='punc_char', type=str, action='append', help='Unicode address of punctuation character to strip; this can used multiple times (e.g., -p 05BE -p 05C0 -p 05C3)')
    parser.add_argument('-r', metavar='rdg_type', type=str, choices=['qere', 'ketiv'], help='Variant reading type to use from <app/> elements.')
    parser.add_argument('-t', metavar='tag', type=str, action='append', help='Local XML tag names of elements to ignore; this can used multiple times (e.g., -t pb -t cb -t lb)')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (the default will use the input file base, suffixed with _normalized).')
    parser.add_argument('input', type=str, help='TEI XML input file to normalize.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace('.xml', '_normalized.xml')
    #Create the parameters for the normalizer:
    ignored_accent_set = set() if args.a is None else set(args.a)
    ignored_punc_set = set() if args.p is None else set([chr(int(p, 16)) for p in args.p])
    preferred_rdg_type = None if args.r is None else args.r
    ignored_tag_set = set() if args.t is None else set(args.t)
    #If 'TEI' is in the ignored tag set, then report an error and exit:
    if 'TEI' in ignored_tag_set:
        print('Error: "TEI" cannot be an ignored element (the entire XML file would be ignored).')
        exit(1)
    #Initialize the normalizer with these parameters:
    normalizer = tei_normalizer(a=ignored_accent_set, p=ignored_punc_set, r=preferred_rdg_type, w=None, t=ignored_tag_set)
    #Parse the input XML document:
    input_xml = et.parse(input_addr)
    #Normalize the input and get the output:
    output_xml = normalizer.normalize(input_xml)
    #Then write it to the output address:
    output_xml.write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    exit(0)

if __name__=="__main__":
    main()
