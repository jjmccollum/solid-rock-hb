#!/usr/bin/env python3

import argparse
from lxml import etree as et
from tei_context_converter import tei_context_converter

"""
Dictionary mapping book numbers to book titles.
"""
book_titles = {
    'B01': 'בראשית',
	'B02': 'שמות',
	'B03': 'ויקרא',
	'B04': 'במדבר',
	'B05': 'דברים',
	'B06': 'יהושע',
	'B07': 'שפטים',
	'B08': 'שמואל א',
	'B09': 'שמואל ב',
	'B10': 'מלכים א',
	'B11': 'מלכים ב',
	'B12': 'ישעיה',
	'B13': 'ירמיה',
	'B14': 'יחזקאל',
	'B15': 'הושע',
	'B16': 'יואל',
	'B17': 'עמוס',
	'B18': 'עבדיה',
	'B19': 'יונה',
	'B20': 'מיכה',
	'B21': 'נחום',
	'B22': 'חבקוק',
	'B23': 'צפניה',
	'B24': 'חגי',
	'B25': 'זכריה',
	'B26': 'מלאכי',
	'B27': 'תהלים',
	'B28': 'משלי',
	'B29': 'איוב',
	'B30': 'שיר השירים',
	'B31': 'רות',
	'B32': 'איכה',
	'B33': 'קהלת',
	'B34': 'אסתר',
	'B35': 'דניאל',
	'B36': 'עזרא',
	'B37': 'נחמיה',
	'B38': 'דברי הימים א',
	'B39': 'דברי הימים ב'
}

"""
Dictionary mapping witness references to sigla.
"""
wit_sigla = {
    '#SR': 'SR',
    '#WLC': 'L'
}

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description='Converts a labeled TEI XML collation to a ConTeXt script and writes the result to output.')
    parser.add_argument('-a', metavar='ignored_app_type', type=str, action='append', help='Variation type to ignore; this can used multiple times (e.g., -a vocalic -a orthographic)')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (the default will use the input file base with the .tex extension).')
    parser.add_argument('input', type=str, help='TEI XML collation file to convert to ConTeXt.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.input
    output_addr = args.o if args.o is not None else input_addr.replace('.xml', '.tex')
    ignored_app_types = set() if args.a is None else set(args.a)
    #Create the parameters for the converter:
    converter_args = {}
    converter_args['book_titles'] = book_titles
    converter_args['wit_sigla'] = wit_sigla
    converter_args['ignored_app_types'] = ignored_app_types
    #Initialize the converter with these parameters:
    converter = tei_context_converter(**converter_args)
    #Parse the input XML document:
    input_xml = et.parse(input_addr)
    #Convert the input and write to output:
    latex = converter.to_context(input_xml)
    #Then write it to the output address:
    output_latex = open(output_addr, 'w', encoding='utf-8')
    output_latex.write(latex)
    output_latex.close()
    exit(0)

if __name__=="__main__":
    main()
