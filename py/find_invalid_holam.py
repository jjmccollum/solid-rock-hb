#!/usr/bin/env python3

import argparse
from lxml import etree as et
import re

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Locates all invalid uses of holam haser in the given TEI XML file.')
    parser.add_argument('input', type=str, help='TEI XML file to check.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    #Parse the input XML document:
    xml = et.parse(input_addr)
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    #Then iterate over all the children of the XML tree's <body/> element:
    body = xml.xpath('//tei:body', namespaces={'tei': tei_ns})[0]
    div_n = ''
    invalid_holam_haser_re = re.compile('[^\u05D5]\u05BA')
    for child in body:
        if child.tag.replace('{%s}' % tei_ns, '') == 'divGen':
            if child.get('n') is not None:
                div_n = child.get('n')
            continue
        if child.tag.replace('{%s}' % tei_ns, '') == 'w':
            if invalid_holam_haser_re.search(child.text) is not None:
                print('Invalid holam haser found at word ' + child.text + ' in div ' + div_n)
    exit(0)

if __name__=="__main__":
    main()
