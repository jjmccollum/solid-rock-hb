#!/usr/bin/env python3

import argparse
from lxml import etree as et
import re

"""
XML namespaces
"""
xml_ns = 'http://www.w3.org/XML/1998/namespace'
tei_ns = 'http://www.tei-c.org/ns/1.0'

#Regular expression for characters to normalize out for lookup purposes 
#(we want to remove everything other than consonants and dagesh):
normalization_re = re.compile('[^\u05BC\u05D0-\u05EA]')
#Dictionary of SRO spelling normalizations:
sro_normalizations = {
    'יהוה': 'יַהְוֶה',
    'ויהוה': 'וְיַהְוֶה',
    'ביהוה': 'בְיַהְוֶה',
    'וּביהוה': 'וּבְיַהְוֶה',
    'בּיהוה': 'בְּיַהְוֶה',
    'ליהוה': 'לְיַהְוֶה',
    'וליהוה': 'וּלְיַהְוֶה',
    'מיהוה': 'מִיַּהְוֶה',
    'וּמיהוה': 'וּמִיַּהְוֶה',
    'שיהוה': 'שִׁיַּהְוֶה',
    'ירוּשלם': 'יְרוּשָׁלֵם',
    'וירוּשלם': 'וִיְרוּשָׁלֵם',
    'בירוּשלם': 'בִירוּשָׁלֵם',
    'וּבירוּשלם': 'וּבִירוּשָׁלֵם',
    'בּירוּשלם': 'בִּירוּשָׁלֵם',
    'לירוּשלם': 'לִירוּשָׁלֵם',
    'ולירוּשלם': 'וְלִירוּשָׁלֵם',
    'מירוּשלם': 'מִירוּשָׁלֵם',
    'וּמירוּשלם': 'וּמִירוּשָׁלֵם'
}
#Dictionary of SRO spelling normalizations for 1 and 2 Chronicles:
sro_normalizations_chron = {
    'יהוה': 'יְהֹוַה',
    'ויהוה': 'וַיהֹוַה',
    'ביהוה': 'בַיהֹוַה',
    'בּיהוה': 'בַּיהֹוַה',
    'ליהוה': 'לַיהֹוַה',
    'מיהוה': 'מֵיְהֹוַה',
    'ירוּשלם': 'יְרוּשָׁלֵם',
    'וירוּשלם': 'וִיְרוּשָׁלֵם',
    'בירוּשלם': 'בִירוּשָׁלֵם',
    'וּבירוּשלם': 'וּבִירוּשָׁלֵם',
    'בּירוּשלם': 'בִּירוּשָׁלֵם',
    'לירוּשלם': 'לִירוּשָׁלֵם',
    'ולירוּשלם': 'וְלִירוּשָׁלֵם',
    'מירוּשלם': 'מִירוּשָׁלֵם',
    'וּמירוּשלם': 'וּמִירוּשָׁלֵם'
}

"""
Normalizes the spelling of all words in the given XML tree that occur in the standard normalization Dictionary.
The XML tree is modified in-place.
"""
def normalize(xml):
    #If this is a tree, then recursively process its root element:
    if not et.iselement(xml):
        normalize(xml.getroot())
        return
    #Proceed for each word element in the XML tree:
    for w in xml.xpath('//tei:w', namespaces={'tei': tei_ns}):
        #Get a copy of this word's text stripped of all unnecessary characters:
        if w.text is None:
            continue
        normalized_text = re.sub(normalization_re, '', w.text)
        #If the normalized text represents a word to be normalized, 
        #then change the text of the word to the normalized spelling:
        if normalized_text in sro_normalizations:
            w.text = sro_normalizations[normalized_text]
    return

"""
Normalizes the spelling of all words in the given XML tree that occur in the normalization Dictionary for Chronicles.
The XML tree is modified in-place.
"""
def normalize_chron(xml):
    #If this is a tree, then recursively process its root element:
    if not et.iselement(xml):
        normalize_chron(xml.getroot())
        return
    #Proceed for each word element in the XML tree:
    for w in xml.xpath('//tei:w', namespaces={'tei': tei_ns}):
        #Get a copy of this word's text stripped of all unnecessary characters:
        if w.text is None:
            continue
        normalized_text = re.sub(normalization_re, '', w.text)
        #If the normalized text represents a word to be normalized, 
        #then change the text of the word to the normalized spelling:
        if normalized_text in sro_normalizations_chron:
            w.text = sro_normalizations_chron[normalized_text]
    return

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Normalizes spellings of words in a TEI XML transcription according to SRO parameters and outputs the result as a TEI XML file.')
    parser.add_argument('--chron', action='store_true', default=False, help='Use alternate spelling normalizations for 1 and 2 Chronicles')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (the default will use the input file base, suffixed with _normalized).')
    parser.add_argument('input', type=str, help='TEI XML input file to normalize.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace('.xml', '_normalized.xml')
    #Parse the input XML document:
    xml = et.parse(input_addr)
    #Normalize its spellings in-place:
    if not args.chron:
        normalize(xml)
    else:
        normalize_chron(xml)
    #Then write it to the output address:
    xml.write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    exit(0)

if __name__=="__main__":
    main()