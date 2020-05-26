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
    '14': 'Ezekiel',
    '15': 'Hosea',
    '16': 'Joel',
    '17': 'Amos',
    '18': 'Obadiah',
    '19': 'Jonah',
    '20': 'Micah',
    '21': 'Nahum',
    '22': 'Habakkuk',
    '23': 'Zephaniah',
    '24': 'Haggai',
    '25': 'Zechariah',
    '26': 'Malachi',
    '27': 'Psalms',
    '28': 'Proverbs',
    '29': 'Job',
    '30': 'Song of Songs',
    '31': 'Ruth',
    '32': 'Lamentations',
    '33': 'Ecclesiastes',
    '34': 'Esther',
    '35': 'Daniel',
    '36': 'Ezra',
    '37': 'Nehemiah',
    '38': '1 Chronicles',
    '39': '2 Chronicles'
}

"""
Regular expressions
"""
FILENAME_REGEX = re.compile('(\d+)_(.*).xml')
PUNC_REGEX = re.compile('([\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7\u05D0-\u05F2\u200C-\u200D\uFB1D-\uFB1F\uFB2A-\uFB4E]*)([\u05BE\u05C0\u05C3\u05C6\u05F3-\u05F4]*)')

def word_to_xml(word):
    """
    Given a unicode String representing a single word and any surrounding punctuation, parse it to a List of XML <w/> and <pc/> elements.
    """
    xml = []
    #Normalize the word:
    normalized = word
    normalized = normalized.replace('/', '') #remove forward slashes separating prefixes and suffixes from word roots
    normalized = ud.normalize('NFC', normalized) #convert decomposed unicode characters to precomposed unicode characters
    #Then separate the word from its trailing punctuation:
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

def wlc_to_itsee(input_addr, output_addr):
    """
    Given the address of an input .xml file in WLC TEI format, reformats and writes the TEI XML to a file with the output address according to ITSEE guidelines.
    """
    print('Parsing text from %s to %s...' % (input_addr, output_addr))
    #Open the input XML tree to be read:
    parser = et.XMLParser(remove_blank_text=True)
    input_tei = et.parse(input_addr, parser=parser)
    #Get the index of the book we'll be writing to:
    match = FILENAME_REGEX.match(os.path.basename(input_addr))
    if match is None or len(match.groups()) < 2 or match.groups()[0] not in BOOK_NAMES:
        print('The input file name is expected to represent the index of the book (e.g., "01_WLC.xml" for Genesis in the WLC).')
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
    #Add a <div/> element for the incipit using the book's Hebrew name:
    hebrewname = input_tei.xpath('//hebrewname')[0]
    incipit_n = book_n + 'incipit'
    incipit = et.Element('div')
    incipit.set('type', 'incipit')
    incipit.set('n', incipit_n)
    book.append(incipit)
    verse = et.Element('ab')
    words = hebrewname.text.split()
    for word in words:
        els = word_to_xml(word)
        for el in els:
            verse.append(el)
    #Add a line break at the end of the incipit:
    lb = et.Element('lb')
    verse.append(lb)
    incipit.append(verse)
    #Then proceed for each element in the file:
    chapter_n = ''
    chapter = None
    verse_n = ''
    verse = None
    app = None
    rdg = None
    ketiv_toggle = False
    qere_toggle = False
    for child in input_tei.getiterator():
        if child.tag == 'c':
            #This is a new chapter:
            ketiv_toggle = False
            qere_toggle = False
            chapter_n = book_n + 'K' + child.get('n')
            chapter = et.Element('div')
            chapter.set('type', 'chapter')
            chapter.set('n', chapter_n)
            book.append(chapter)
            continue
        if child.tag == 'v':
            #This is a new verse:
            ketiv_toggle = False
            qere_toggle = False
            #Since multiple documentary sources may exist within the same verse, one verse may be repeated;
            #only add a new <ab/> element if the verse number changes:
            new_verse_n = chapter_n + 'V' + child.get('n')
            if new_verse_n != verse_n:
                verse_n = new_verse_n
                verse = et.Element('ab')
                verse.set('n', verse_n)
                chapter.append(verse)
            continue
        if child.tag == 'k':
            #This is a word of a ketiv reading; create new <app/> and <rdg/> elements, if we haven't already:
            qere_toggle = False
            if not ketiv_toggle:
                ketiv_toggle = True
                app = et.Element('app')
                verse.append(app)
                rdg = et.Element('rdg')
                rdg.set('type', 'ketiv')
                app.append(rdg)
            #Check for any child elements included within the word:
            text = child.text if child.text is not None else ''
            for grandchild in child.getchildren():
                #If this word contains stylized letters in a child <s/> element, then append them to this word:
                if grandchild.tag == 's':
                    text += grandchild.text
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
                #If this word contains a note in a child <x/> element, then append any trailing letters to this word:
                if grandchild.tag == 'x':
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
            els = word_to_xml(text)
            for el in els:
                rdg.append(el)
            continue
        if child.tag == 'q':
            #This is a word of a qere reading; if a ketiv reading was not present before it, then create an <app/> element and an empty <rdg/> element:
            if not ketiv_toggle and not qere_toggle:
                ketiv_toggle = True
                app = et.Element('app')
                verse.append(app)
                rdg = et.Element('rdg')
                rdg.set('type', 'ketiv')
                app.append(rdg)
            else:
                ketiv_toggle = False
            #If a ketiv reading has already been processed, then create a new <rdg/> element, if we haven't already:
            if not qere_toggle:
                qere_toggle = True
                rdg = et.Element('rdg')
                rdg.set('type', 'qere')
                app.append(rdg)
            #Check for any child elements included within the word:
            text = child.text if child.text is not None else ''
            for grandchild in child.getchildren():
                #If this word contains stylized letters in a child <s/> element, then append them to this word:
                if grandchild.tag == 's':
                    text += grandchild.text
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
                #If this word contains a note in a child <x/> element, then append any trailing letters to this word:
                if grandchild.tag == 'x':
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
            els = word_to_xml(text)
            for el in els:
                rdg.append(el)
            continue
        if child.tag == 'w':
            #This is a normal word:
            ketiv_toggle = False
            qere_toggle = False
            text = child.text
            #If multiple documentary sources exist within the same verse, then ignore the placeholders:
            if text == '.':
                continue
            #Check for any child elements included within the word:
            for grandchild in child.getchildren():
                #If this word contains stylized letters in a child <s/> element, then append them to this word:
                if grandchild.tag == 's':
                    text += grandchild.text
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
                #If this word contains a note in a child <x/> element, then append any trailing letters to this word:
                if grandchild.tag == 'x':
                    if grandchild.tail is not None:
                        text += grandchild.tail.strip()
            #If the word contains a space followed by punctuation, then remove the space:
            text = text.replace(' ', '')
            els = word_to_xml(text)
            for el in els:
                verse.append(el)
            continue
        if child.tag == 's':
            #Ignore, as we've already processed this:
            continue
        if child.tag == 'x':
            #Ignore, as we've already processed this:
            continue
        if child.tag == 'pe':
            #This is an open section break:
            ketiv_toggle = False
            qere_toggle = False
            lb = et.Element('lb')
            lb.set('type', 'open')
            verse.append(lb)
            continue
        if child.tag == 'samekh':
            #This is a closed section break:
            ketiv_toggle = False
            qere_toggle = False
            space = et.Element('space')
            space.set('type', 'closed')
            verse.append(space)
            continue
    #Then clean up the namespaces for the XML:
    et.cleanup_namespaces(tei)
    #Then write to output:
    et.ElementTree(tei).write(output_addr, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return

def main():
    """
    Entry point to the script. Parses command-line arguments, reads in an input .txt file and writes to an output TEI XML file.
    """
    parser = argparse.ArgumentParser(description='Reformat and write a TEI XML input file in the WLC formatting to a TEI XML output file formatted according to ITSEE guidelines.')
    parser.add_argument('-i', metavar='input', type=str, help='Input file address in the form {book_number}_{witness_id}.txt. (example: 01_WLC.xml).')
    parser.add_argument('-o', metavar='output', type=str, help='Output file address.')
    args = parser.parse_args()
    #Parse the I/O arguments:
    input_addr = args.i
    output_addr = args.o
    if not input_addr:
        print('ERROR: input file base must be provided after -i flag.')
        exit(-1)
    if not input_addr.endswith('.xml'):
        print('The input file must be a .xml file.')
        exit(-1)
    if not output_addr:
        print('ERROR: output file must be provided after -o flag.')
        exit(-1)
    if not output_addr.endswith('.xml'):
        print('The output file must be a .xml file.')
        exit(-1)
    #Then run the main method:
    wlc_to_itsee(input_addr, output_addr)
    return

if __name__=="__main__":
    main()
