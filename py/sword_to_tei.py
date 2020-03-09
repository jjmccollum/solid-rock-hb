#!/usr/bin/env python3

import argparse, os
from lxml import etree as et
import re
import unicodedata as ud

"""
XML namespaces
"""
XML_NS = 'http://www.w3.org/XML/1998/namespace'
TEI_NS = 'http://www.tei-c.org/ns/1.0'

"""
Book index-to-book name Dictionary.
"""
BOOK_NAMES = {
    '01': 'Genesis',
    '02': 'Exodus',
    '03': 'Leviticus',
    '04': 'Numbers',
    '05': 'Deuteronomy',
    '06': 'Joshua',
    '07': 'Judges',
    '08': '1 Samuel',
    '09': '2 Samuel',
    '10': '1 Kings',
    '11': '2 Kings',
    '12': 'Isaiah',
    '13': 'Jeremiah',
    '14': 'Ezekiel'
}

"""
Regular expressions
"""
FILENAME_REGEX = re.compile('(\d+)_(.*).txt')
PUNC_REGEX = re.compile('([\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7\u05D0-\u05F2\u200C-\u200D\uFB1D-\uFB1F\uFB2A-\uFB4E]*)([\u05BE\u05C0\u05C3\u05C6\u05F3-\u05F4]*)')
CHAPTER_REGEX = re.compile('Chapter (\d+)')
VERSE_REGEX = re.compile('\[(\d+)\]')
SECTION_BREAK_REGEX = re.compile('\{(\w)\}')

def word_to_xml(word):
    """
    Given a unicode String representing a single word and any surrounding punctuation, parse it to a List of XML <w/> and <pc/> elements.
    """
    xml = []
    normalized = ud.normalize('NFC', word) #convert decomposed unicode characters to precomposed unicode characters
    groups = PUNC_REGEX.match(normalized).groups()
    word_text = groups[0]
    trailing_punc = groups[1]
    #Process the word itself:
    if word_text != '':
        w = et.Element('w')
        w.text = word_text
        w.tail = '' #add an empty tail to ensure printing on the same line
        xml.append(w)
    #Process any trailing punctuation:
    if trailing_punc != '':
        #Create an element for each trailing punctuation mark separately:
        for punc in list(trailing_punc):
            pc = et.Element('pc')
            pc.text = punc
            pc.tail = '' #add an empty tail to ensure printing on the same line
            xml.append(pc)
    return xml

def text_to_tei(input_addr, output_addr):
    """
    Given an input .txt file address and an output .xml file address, parses and normalizes the unicode text in the input and writes it to the output in TEI format.
    """
    print('Parsing text from %s to %s...' % (input_addr, output_addr))
    #Open the input file to be read:
    input_file = open(input_addr, 'r')
    #Get the index of the book we'll be writing to:
    match = FILENAME_REGEX.match(os.path.basename(input_addr))
    if match is None or len(match.groups()) < 2 or match.groups()[0] not in BOOK_NAMES:
        print('The input file name is expected to represent the index of the book (e.g., "01_WLC.txt" for Genesis in the WLC).')
        exit(-1)
    wit_ind = match.groups()[1]
    book_ind = match.groups()[0]
    #Now we'll begin constructing the XML tree to be output.
    #First, define the namespace to use:
    nsmap={None: TEI_NS}
    #Under this, add a <TEI/> element to be populated later:
    tei = et.Element('{%s}TEI' % TEI_NS, nsmap=nsmap)
    #First, add a <teiHeader/> element under the TEI element:
    teiHeader = et.Element('{%s}teiHeader' % TEI_NS)
    tei.append(teiHeader)
    #Under this, add a <fileDesc/> element:
    fileDesc = et.Element('{%s}fileDesc' % TEI_NS)
    teiHeader.append(fileDesc)
    #Under this, add a <titleStmt/> element:
    titleStmt = et.Element('{%s}titleStmt' % TEI_NS)
    fileDesc.append(titleStmt)
    #Under this, add a <title/> element:
    title = et.Element('{%s}title' % TEI_NS)
    title.text = 'A transcription of %s in %s' % (BOOK_NAMES[book_ind], wit_ind)
    titleStmt.append(title)
    #Next, add a <title/> element for the document ID:
    title_document = et.Element('{%s}title' % TEI_NS)
    title_document.set('type', 'document')
    title_document.set('n', wit_ind)
    title_document.text = wit_ind
    titleStmt.append(title_document)
    #Next, add a <publicationStmt/> element under the fileDesc:
    publicationStmt = et.Element('{%s}publicationStmt' % TEI_NS)
    p = et.Element('p')
    p.text = 'Temporary publicationStmt for validation'
    publicationStmt.append(p)
    fileDesc.append(publicationStmt)
    #Next, add a <sourceDesc/> element under the fileDesc:
    sourceDesc = et.Element('{%s}sourceDesc' % TEI_NS)
    p = et.Element('p')
    p.text = 'Temporary sourceDesc for validation'
    sourceDesc.append(p)
    fileDesc.append(sourceDesc)
    #Then, add a <text/> element under the TEI element:
    text = et.Element('{%s}text' % TEI_NS)
    text.set('{%s}lang' % XML_NS, 'he')
    tei.append(text)
    #Under this, add a <body/> element:
    body = et.Element('body')
    text.append(body)
    #Add a <div/> element for the book under the body element:
    book_n = 'B' + book_ind
    book = et.Element('div')
    book.set('type', 'book')
    book.set('n', book_n)
    body.append(book)
    #Then proceed for each line of text in the file:
    chapter_n = ''
    chapter = None
    verse_n = ''
    verse = None
    app = None
    rdg = None
    ketiv_toggle = False
    qere_toggle = False
    for line in input_file:
        #Check for any division changes first:
        if line.strip() == '':
            #Skip all empty lines:
            continue
        if chapter_n == '':
            #The incipit is the first line:
            incipit_n = book_n + 'incipit'
            incipit = et.Element('div')
            incipit.set('type', 'incipit')
            incipit.set('n', incipit_n)
            book.append(incipit)
            verse = et.Element('ab')
            words = line.strip().split()
            for word in words:
                els = word_to_xml(word)
                for el in els:
                    verse.append(el)
            #Add a line break at the end of the incipit:
            lb = et.Element('lb')
            verse.append(lb)
            incipit.append(verse)
            chapter_n = incipit_n #add this so we skip this if block next time
            continue
        elif CHAPTER_REGEX.match(line.strip()) is not None:
            #If it is a chapter start, then add a <div/> element for the new chapter:
            groups = CHAPTER_REGEX.match(line.strip()).groups()
            chapter_n = book_n + 'K' + groups[0]
            chapter = et.Element('div')
            chapter.set('type', 'chapter')
            chapter.set('n', chapter_n)
            book.append(chapter)
            continue
        #Then strip the line of surrounding whitespace and proceed for each word in the line:
        words = line.strip().split()
        for word in words:
            #Check if this token represents a verse index, a section break, or a proper word:
            if VERSE_REGEX.match(word) is not None:
                #If it is a verse start, then add a new verse element:
                groups = VERSE_REGEX.match(word).groups()
                verse_n = chapter_n + 'V' + groups[0]
                verse = et.Element('ab')
                verse.set('n', verse_n)
                chapter.append(verse)
            elif SECTION_BREAK_REGEX.match(word) is not None:
                #If it is a section break, then add the corresponding line break:
                #TODO: Format open and closed sections differently?
                groups = SECTION_BREAK_REGEX.match(word).groups()
                if groups[0] == 'פ':
                    lb = et.Element('lb')
                    lb.set('type', 'open')
                    verse.append(lb)
                elif groups[0] == 'ס':
                    space = et.Element('space')
                    space.set('type', 'closed')
                    verse.append(space)
                elif groups[0] == 'ר':
                    lb = et.Element('lb')
                    lb.set('type', 'song')
                    verse.append(lb)
                elif groups[0] == 'ש':
                    pb = et.Element('pb')
                    pb.set('type', 'page')
                    verse.append(pb)
            else:
                #If we're encountering a ketiv phrase (surrounded by curly braces) or qere phrase (surrounded by parentheses), then create an <app/> element to store the difference:
                if word.startswith('{'):
                    ketiv_toggle = True
                    word = word.strip('{')
                    app = et.Element('app')
                    verse.append(app)
                    rdg = et.Element('rdg')
                    rdg.set('type', 'ketiv')
                    app.append(rdg)
                elif word.startswith('('):
                    qere_toggle = True
                    word = word.strip('(')
                    rdg = et.Element('rdg')
                    rdg.set('type', 'qere')
                    app.append(rdg)
                if ketiv_toggle:
                    if word.endswith('}'):
                        ketiv_toggle = False
                        word = word.strip('}')
                    els = word_to_xml(word)
                    for el in els:
                        rdg.append(el)
                elif qere_toggle:
                    if word.endswith(')'):
                        qere_toggle = False
                        word = word.strip(')')
                    els = word_to_xml(word)
                    for el in els:
                        rdg.append(el)
                else:
                    els = word_to_xml(word)
                    for el in els:
                        verse.append(el)
    #Then clean up the namespaces for the XML:
    et.cleanup_namespaces(tei)
    #Then write to output:
    et.ElementTree(tei).write(output_addr, doctype='<!DOCTYPE TEI>', encoding='utf-8', xml_declaration=True, pretty_print=True)
    return

def main():
    """
    Entry point to the script. Parses command-line arguments, reads in an input .txt file and writes to an output TEI XML file.
    """
    parser = argparse.ArgumentParser(description='Normalize a Unicode transcription in .txt format copied from a SWORD module and output a corresponding transcription in TEI XML format.')
    parser.add_argument('-i', metavar='input', type=str, help='Input file address in the form {book_number}_{witness_id}.txt. (example: 01_WLC.txt)')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address (example: 01_WLC.xml)')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.i
    output_addr = args.o
    if not input_addr:
        print('ERROR: input file base must be provided after -i flag.')
        exit(-1)
    if not input_addr.endswith('.txt'):
        print('The input file must be a .txt file.')
        exit(-1)
    if not output_addr:
        print('ERROR: output file must be provided after -o flag.')
        exit(-1)
    if not output_addr.endswith('.xml'):
        print('The output file must be a .xml file.')
        exit(-1)
    #Then run the main method:
    text_to_tei(input_addr, output_addr)
    return

if __name__=="__main__":
    main()
