#!/usr/bin/env python3

import argparse
from lxml import etree as et
import re
from tei_normalizer import tei_normalizer

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Locates all unpointed Hebrew words in the given TEI XML file.')
    parser.add_argument('input', type=str, help='TEI XML file to check.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    #Initialize a normalizer:
    ignored_accent_set = set(['cantillation', 'pointing', 'extraordinaire'])
    normalizer = tei_normalizer(**{'a': ignored_accent_set, 'p': set(), 'r': None, 't': None})
    #Parse the input XML document:
    xml = et.parse(input_addr)
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    #Then iterate over all the children of the XML tree's <body/> element:
    body = xml.xpath('//tei:body', namespaces={'tei': tei_ns})[0]
    div_n = ''
    for child in body:
        if child.tag.replace('{%s}' % tei_ns, '') == 'milestone':
            if child.get('n') is not None:
                div_n = child.get('n')
            continue
        if child.tag.replace('{%s}' % tei_ns, '') == 'w':
            if normalizer.format_text(child.text) == child.text:
                print('Unpointed word ' + child.text + ' in div ' + div_n)
    exit(0)

if __name__=="__main__":
    main()
