#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_collator import tei_collator

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Collates one or more TEI XML transcriptions against a TEI XML transcription with desired levels of normalization and outputs the result as a TEI XML file.')
    parser.add_argument('-a', metavar='accent_type', type=str, action='append', choices=['cantillation', 'pointing', 'extraordinaire'], help='Names of accentuation sets to normalize out for collation; this can be used multiple times (e.g., -a cantillation -a extraordinaire)')
    parser.add_argument('-t', metavar='tag', type=str, action='append', help='Local XML tag names of elements to ignore for collation; this can used multiple times (e.g., -t pb -t cb -t lb)')
    parser.add_argument('-l', metavar='level', type=str, help='Textual division level (e.g., book, chapter, verse) to group tokens for collation; collation at higher levels will take longer')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (default: collation.xml)')
    parser.add_argument('lemma', type=str, help='TEI XML transcription to use as the lemma text.')
    parser.add_argument('witness', type=str, nargs='+', help='TEI XML transcriptions to collate against the lemma text.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    lemma_addr = args.lemma
    witness_addrs = args.witness
    output_addr = args.o if args.o is not None else 'collation.xml'
    #Create the parameters for the normalizer:
    ignored_accent_set = set() if args.a is None else set(args.a)
    ignored_tag_set = set() if args.t is None else set(args.t)
    #Set the division level for collation:
    level = 'verse' if args.l is None else args.l
    #If 'TEI' is in the ignored tag set, then report an error and exit:
    if 'TEI' in ignored_tag_set:
        print('Error: "TEI" cannot be an ignored element (the entire XML file would be ignored).')
        exit(1)
    #Initialize the collator with these parameters:
    collator = tei_collator(a=ignored_accent_set, t=ignored_tag_set, l=level)
    #Read in the XML of the lemma and the witnesses:
    collator.read_witness(lemma_addr)
    for witness_addr in witness_addrs:
        collator.read_witness(witness_addr)
    #Collate the witnesses:
    collator.collate()
    #Augment the lemma XML with the collation data:
    collator.augment_lemma()
    #Then write the augmented lemma XML to output:
    collator.lemma_xml.write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    exit(0)

if __name__=="__main__":
    main()
