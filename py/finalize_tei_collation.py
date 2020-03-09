#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_collation_editor import tei_collation_editor
from tei_labeler import tei_labeler

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Resegments, labels, and indexes the apparatus elements of a TEI XML collation and outputs the result as a TEI XML file.')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (the default will use the input file base, suffixed with _finalized).')
    parser.add_argument('input', type=str, help='TEI XML collation file to update.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace('.xml', '_finalized.xml')
    #Initialize the editor and labeler:
    editor = tei_collation_editor()
    labeler = tei_labeler()
    #Parse the input XML document:
    xml = et.parse(input_addr)
    #Make sure the resegmentation is valid:
    print('Validating resegmentation of XML...')
    valid = editor.validate(xml)
    if not valid:
        print('Resegmentation is not valid; exiting...')
        exit(1)
    #Otherwise, update the apparatus boundaries in place:
    print('Resegmentation is valid; updating apparatus boundaries...')
    editor.update_boundaries(xml)
    #Then label the resegmented apparatus elements in place:
    print('Labeling apparatus elements...')
    labeler.label(xml)
    #Then write the updated XML to output:
    xml.write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    exit(0)

if __name__=="__main__":
    main()
