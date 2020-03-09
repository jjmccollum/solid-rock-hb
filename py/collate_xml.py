#!/usr/bin/env python3

import argparse
from lxml import etree as et
import unicodedata as ud
import re
import json
import collatex as cx

"""
XML namespaces
"""
XML_NS = 'http://www.w3.org/XML/1998/namespace'
TEI_NS = 'http://www.tei-c.org/ns/1.0'
CX_NS = 'http://interedition.eu/collatex/ns/1.0'

"""
Regular expressions
"""
CANTILLATION_REGEX = re.compile('[\u0591-\u05AF\u200C-\u200D]')
POINTING_REGEX = re.compile('[\u05B0-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7\u200C-\u200D]')
BOOK_REGEX = re.compile('B(\d+)')
CHAPTER_REGEX = re.compile('B(\d+)K(\d+)')
VERSE_REGEX = re.compile('B(\d+)K(\d+)V(\d+)')
"""
Given an XML tree, returns the same tree with all namespace prefixes removed.
Thanks to har07 at https://stackoverflow.com/questions/30232031/how-can-i-strip-namespaces-out-of-an-lxml-tree/30233635 for this code.
"""
def strip_ns_prefix(tree):
    #Use an xpath query to get all elements with a nontrivial namespace (e.g., {http://www.tei-c.org/ns/1.0}),
    #then remove the namespace from the tag of each such element:
    for element in tree.xpath("descendant-or-self::*[namespace-uri()!='']"):
        element.tag = et.QName(element).localname
    return tree
"""
Utility method for transforming a book index to a numerical tuple.
"""
def book_to_tuple(s):
    groups = BOOK_REGEX.match(s).groups()
    book_ind = int(groups[0])
    return (book_ind,) #comma is necessary to make this a tuple
"""
Utility method for transforming a chapter index to a numerical tuple.
"""
def chapter_to_tuple(s):
    groups = CHAPTER_REGEX.match(s).groups()
    book_ind = int(groups[0])
    chapter_ind = int(groups[1])
    return (book_ind, chapter_ind)
"""
Utility method for transforming a verse index to a numerical tuple.
"""
def verse_to_tuple(s):
    groups = VERSE_REGEX.match(s).groups()
    book_ind = int(groups[0])
    chapter_ind = int(groups[1])
    verse_ind = int(groups[2])
    return (book_ind, chapter_ind, verse_ind)
"""
An element representing a Witness in TEI XML format, complete with its text.
"""
class Witness:
    def __init__(self, tei):
        self.xml = strip_ns_prefix(tei) #get the XML tree without the namespace
        #Get the Gregory-Aland number identifying this Witness:
        self.ga_id = self.xml.xpath("//title[@type='document']")[0].get('n')
        #Populate a Set of distinct verse indices contained in this Witness:
        self.verse_indices = set()
        children = self.xml.xpath('//ab')
        for child in children:
            n = child.get('n')
            if n is not None:
                self.verse_indices.add(n)
"""
An element representing a book of text. It is the largest division of text in a Witness and may contain Chapters.
"""
class Book:
    def __init__(self, div):
        self.xml = div
"""
An element representing a chapter of text. It occurs within a Book and may contain Verses or other document divisions (e.g., Incipits and Explicits).
"""
class Chapter:
    def __init__(self, div):
        self.xml = div
"""
An element representing a verse of text. It occurs within a Chapter and may contain Words or Apparatuses.
"""
class Verse:
    def __init__(self, ab):
        self.xml = ab
    def tokenize(self, params):
        """
        Returns a List of Word-level token Dictionaries contained within this Verse, with each Dictionary containing raw and normalized representations of the corresponding Word.
        """
        tokens = []
        ab = self.xml
        children = ab.getchildren()
        for child in children:
            #If this is a Word, then process it directly:
            if child.tag == 'w':
                w = Word(child)
                t = w.format(params) #formatted text (may or may not include vowels and cantillation marks)
                n = w.normalize() #normalized text (always stripped of vowels and cantillation marks)
                token = {'t': t, 'n': n}
                tokens.append(token)
            #If it is punctuation, then process it only if it is not being normalized out:
            elif child.tag == 'pc':
                if not params['normalize_punc']:
                    pc = Punctuation(child)
                    t = pc.format(params)
                    n = pc.normalize()
                    token = {'t': t, 'n': n}
                    tokens.append(token)
            #If it is a break, then process it only if it is not being normalized out:
            elif child.tag in ['space', 'lb', 'cb', 'pb']:
                if not params['normalize_breaks']:
                    b = Break(child)
                    t = b.format(params)
                    n = b.normalize()
                    token = {'t': t, 'n': n}
                    tokens.append(token)
            #Otherwise, if it is an Apparatus, then recursively process the Words in the original Reading:
            elif child.tag == 'app':
                app = Apparatus(child)
                tokens += app.tokenize(params)
        #If the witness is extant for this verse, but omits it, then indicate this:
        if len(tokens) == 0:
            tokens.append({'t': '', 'n': 'omit'})
        return tokens
"""
An element representing a set of two or more Readings.
"""
class Apparatus:
    def __init__(self, app):
        self.xml = app
    def tokenize(self, params):
        """
        Returns a List of Word-level token Dictionaries contained within this Apparatus, with each Dictionary containing raw and normalized representations of the corresponding Word.
        """
        tokens = []
        app = self.xml
        children = app.getchildren()
        for child in children:
            #Only use ketiv readings:
            #TODO: Separate out corrections for collation?
            if child.tag == 'rdg' and child.get('type') == 'ketiv':
                rdg = Reading(child)
                tokens = rdg.tokenize(params)
                break
        return tokens
"""
A element representing the text of a first hand, corrector, or alternate source, and it contains one or more Words.
"""
class Reading:
    def __init__(self, rdg):
        self.xml = rdg
    """
    Returns a List of Word-level token Dictionaries contained within this Reading, with each Dictionary containing raw and normalized representations of the corresponding Word.
    """
    def tokenize(self, params):
        tokens = []
        rdg = self.xml
        children = rdg.getchildren()
        for child in children:
            #If this is a Word, then process it directly:
            if child.tag == 'w':
                w = Word(child)
                t = w.format(params) #formatted text (may or may not include vowels and cantillation marks)
                n = w.normalize() #normalized text (always stripped of vowels and cantillation marks)
                token = {'t': t, 'n': n}
                tokens.append(token)
            #If it is punctuation, then process it only if it is not being normalized out:
            elif child.tag == 'pc':
                if not params['normalize_punc']:
                    pc = Punctuation(child)
                    t = pc.format(params)
                    n = pc.normalize()
                    token = {'t': t, 'n': n}
                    tokens.append(token)
            #If it is a break, then process it only if it is not being normalized out:
            elif child.tag in ['space', 'lb', 'cb', 'pb']:
                if not params['normalize_breaks']:
                    b = Break(child)
                    t = b.format(params)
                    n = b.normalize()
                    token = {'t': t, 'n': n}
                    tokens.append(token)
            #Otherwise, if it is an Apparatus, then recursively process the Words in the original Reading:
            elif child.tag == 'app':
                app = Apparatus(child)
                tokens += app.tokenize(params)
        return tokens
"""
An element representing a basic token of text. It may contain a Gap, or Unclear or Supplied portions.
"""
class Word:
    def __init__(self, w):
        self.xml = w
    """
    Return a formatted String representing this Word.
    """
    def format(self, params):
        t = self.xml.text
        t = t.strip() #remove surrounding whitespace
        t = ud.normalize('NFKD', t) #decompose any precomposed unicode characters
        t = re.sub(CANTILLATION_REGEX, '', t) if params['normalize_cantillation'] else t #conditionally remove cantillation
        t = re.sub(POINTING_REGEX, '', t) if params['normalize_pointing'] else t #conditionally remove pointing
        t = ud.normalize('NFC', t) #re-compose the decomposed unicode characters
        #A Word should never have any tail text, so return the formatted String constructed so far, plus an additional space (to make the collation readable):
        t += ' '
        return t
    """
    Return a normalized String representing this Word.
    """
    def normalize(self):
        n = self.xml.text
        n = n.strip() #remove surrounding whitespace
        n = ud.normalize('NFKD', n) #decompose any precomposed unicode characters
        n = re.sub(CANTILLATION_REGEX, '', n) #remove cantillation
        n = re.sub(POINTING_REGEX, '', n) #remove pointing
        n = ud.normalize('NFC', n) #re-compose the decomposed unicode characters
        return n
"""
An element representing a basic token of punctuation.
"""
class Punctuation:
    def __init__(self, pc):
        self.xml = pc
    """
    Return a formatted String representing this Punctuation.
    """
    def format(self, params):
        t = self.xml.text + ' '
        return t
    """
    Return a normalized String representing this Punctuation.
    """
    def normalize(self):
        n = self.xml.text
        return n
"""
An element representing a section break.
"""
class Break:
    def __init__(self, b):
        self.xml = b
    """
    Return a formatted String representing this Break.
    """
    def format(self, params):
        t = ''
        b = self.xml
        break_type = b.get('type')
        if break_type == 'open':
            t = '{פ}'
        elif break_type == 'closed':
            t = '{ס}'
        elif break_type == 'song':
            t = '{ר}'
        elif break_type == 'page':
            t = '{ש}'
        t += ' '
        return t
    """
    Return a normalized String representing this Break.
    """
    def normalize(self):
        n = ''
        b = self.xml
        break_type = b.get('type')
        if break_type == 'open':
            n = '{פ}'
        elif break_type == 'closed':
            n = '{ס}'
        elif break_type == 'song':
            n = '{ר}'
        elif break_type == 'page':
            n = '{ש}'
        return n
"""
Given a List of Witnesses, returns an ordered List of verse indices shared by all of them.
"""
def get_extant_verses(witnesses):
    #First, get the union of all witnesses' Sets of verse indices:
    verses = set()
    for witness in witnesses:
        verses = verses.union(witness.verse_indices)
    #Next, cast this Set as a List and sort it in lexicographical order:
    verses = list(verses)
    verses.sort(key=verse_to_tuple)
    return verses
"""
Given a List of Witnesses and a Dictionary of command-line parameters, returns a <div/> element containing a collation of their incipits in TEI XML format.
Witnesses that lack an incipit are left out of the collation.
"""
def collate_incipit(witnesses, params):
    print('Collating incipit...')
    #Prepare a verse index String to be set later:
    verse_index = ''
    #Prepare a List of witness IDs to be populated later:
    wit_ids = []
    #Populate a Dictionary with tokens from each extant witness:
    collation = {'witnesses': []}
    for witness in witnesses:
        #Get the ID of this witness:
        wit_id = witness.ga_id
        #Check if the witness has the given verse:
        children = witness.xml.xpath("//div[@type='incipit']")
        if len(children) > 0:
            #If it does, then add it to the list of extant witnesses:
            wit_ids.append('#' + wit_id)
            #Then tokenize its text:
            child = children[0]
            verse_index = child.get('n')
            grandchildren = child.xpath('./ab')
            if len(grandchildren) > 0:
                grandchild = grandchildren[0]
                verse = Verse(grandchild)
                tokens = verse.tokenize(params)
                collation['witnesses'].append({'id': wit_id, 'tokens': tokens})
    #If none of the witnesses is extant here, then return nothing:
    if len(wit_ids) == 0:
        return
    #Otherwise, convert the populated Dictionary to a JSON Object:
    collation = json.loads(json.dumps(collation))
    #Now use CollateX to collate:
    tei = cx.collate(collation, output='tei')
    #Then parse the XML:
    apparatus = et.XML(tei)
    #Loop through all elements of the collation and strip surrounding whitespace from their texts and tails:
    for child in apparatus.getiterator():
        if child.text is not None:
            child.text = child.text.strip()
        if child.tail is not None:
            child.tail = child.tail.strip()
    #If we're marking lemma readings, then do so here:
    if params['lemma']:
        lem_wit_id = '#' + witnesses[0].ga_id
        for rdg in apparatus.xpath('//tei:rdg', namespaces={'tei': TEI_NS}):
            rdg_wit_ids = rdg.get('wit').split()
            if lem_wit_id in rdg_wit_ids:
                rdg.tag = '{%s}lem' % TEI_NS
    #Then parse the XML and reformat it so it is contained within a <div/> element and an <ab/> element for this verse:
    div = et.Element('div')
    div.set('type', 'incipit')
    div.set('n', verse_index)
    apparatus.tag = '{%s}ab' % TEI_NS
    apparatus.set('wit', ' '.join(wit_ids)) #WARNING: the TEI standard doesn't encourage specifying a 'wit' attribute for <ab/> elements.
    div.append(apparatus)
    return div
"""
Given a List of Witnesses and a Dictionary of command-line parameters, returns a <div/> element containing a collation of their explicits in TEI XML format.
Witnesses that lack an explicit are left out of the collation.
"""
def collate_explicit(witnesses, params):
    print('Collating explicit...')
    #Prepare a verse index String to be set later:
    verse_index = ''
    #Prepare a List of witness IDs to be populated later:
    wit_ids = []
    #Populate a Dictionary with tokens from each extant witness:
    collation = {'witnesses': []}
    for witness in witnesses:
        #Get the ID of this witness:
        wit_id = witness.ga_id
        #Check if the witness has the given verse:
        children = witness.xml.xpath("//div[@type='explicit']")
        if len(children) > 0:
            #If it does, then add it to the list of extant witnesses:
            wit_ids.append('#' + wit_id)
            #Then tokenize its text:
            child = children[0]
            verse_index = child.get('n')
            grandchildren = child.xpath('./ab')
            if len(grandchildren) > 0:
                grandchild = grandchildren[0]
                verse = Verse(grandchild)
                tokens = verse.tokenize(params)
                collation['witnesses'].append({'id': wit_id, 'tokens': tokens})
    #If none of the witnesses is extant here, then return nothing:
    if len(wit_ids) == 0:
        return
    #Convert the populated Dictionary to a JSON Object:
    collation = json.loads(json.dumps(collation))
    #Now use CollateX to collate:
    tei = cx.collate(collation, output='tei')
    #Then parse the XML:
    apparatus = et.XML(tei)
    #Loop through all elements of the collation and strip surrounding whitespace from their texts and tails:
    for child in apparatus.getiterator():
        if child.text is not None:
            child.text = child.text.strip()
        if child.tail is not None:
            child.tail = child.tail.strip()
    #If we're marking lemma readings, then do so here:
    if params['lemma']:
        lem_wit_id = '#' + witnesses[0].ga_id
        for rdg in apparatus.xpath('//tei:rdg', namespaces={'tei': TEI_NS}):
            rdg_wit_ids = rdg.get('wit').split()
            if lem_wit_id in rdg_wit_ids:
                rdg.tag = '{%s}lem' % TEI_NS
    #Then parse the XML and reformat it so it is contained within a <div/> element and an <ab/> element for this verse:
    div = et.Element('div')
    div.set('type', 'explicit')
    div.set('n', verse_index)
    apparatus.tag = '{%s}ab' % TEI_NS
    apparatus.set('wit', ' '.join(wit_ids)) #WARNING: the TEI standard doesn't encourage specifying a 'wit' attribute for <ab/> elements.
    div.append(apparatus)
    return div
"""
Given a List of Witnesses, a verse index (e.g., 'B04K21V2'), and a Dictionary of command-line parameters, returns an <ab/> element containing a collation of their texts in TEI XML format.
Witnesses that lack the given verse are left out of the collation.
"""
def collate_verse(witnesses, verse_index, params):
    print('Collating %s...' % verse_index)
    #Prepare a List of witness IDs to be populated later:
    wit_ids = []
    #Populate a Dictionary with tokens from each extant witness:
    collation = {'witnesses': []}
    for witness in witnesses:
        #Get the ID of this witness:
        wit_id = witness.ga_id
        #Check if the witness has the given verse:
        children = witness.xml.xpath("//ab[@n='" + verse_index + "']")
        if len(children) > 0:
            #If it does, then add it to the list of extant witnesses:
            wit_ids.append('#' + wit_id)
            #Then tokenize its text:
            verse = Verse(children[0])
            tokens = verse.tokenize(params)
            collation['witnesses'].append({'id': wit_id, 'tokens': tokens})
    #Convert the populated Dictionary to a JSON Object:
    collation = json.loads(json.dumps(collation))
    #Now use CollateX to collate:
    tei = cx.collate(collation, output='tei')
    #Then parse the XML:
    apparatus = et.XML(tei)
    #Loop through all elements of the collation and strip surrounding whitespace from their texts and tails:
    for child in apparatus.getiterator():
        if child.text is not None:
            child.text = child.text.strip()
        if child.tail is not None:
            child.tail = child.tail.strip()
    #If we're marking lemma readings, then do so here:
    if params['lemma']:
        lem_wit_id = '#' + witnesses[0].ga_id
        for rdg in apparatus.xpath('//tei:rdg', namespaces={'tei': TEI_NS}):
            rdg_wit_ids = rdg.get('wit').split()
            if lem_wit_id in rdg_wit_ids:
                rdg.tag = '{%s}lem' % TEI_NS
    #Then parse the XML and reformat it so it is contained within an <ab/> element for this verse:
    apparatus.tag = '{%s}ab' % TEI_NS
    apparatus.set('n', verse_index)
    apparatus.set('wit', ' '.join(wit_ids)) #WARNING: the TEI standard doesn't encourage specifying a 'wit' attribute for <ab/> elements.

    return apparatus
"""
Given a List of Witnesses and a Dictionary of command-line parameters, returns a CollateX <apparatus/> element containing a full verse-by-verse collation of their texts in TEI XML format, 
including book, chapter, and verse divisions.
"""
def collate(witnesses, params):
    #Define the namespace to use:
    nsmap={None: TEI_NS, 'cx': CX_NS}
    #Initialize a CollateX <apparatus/> element to be populated later:
    apparatus = et.Element('{%s}apparatus' % CX_NS, nsmap=nsmap)
    #Under this, add a <TEI> element to be populated later:
    tei = et.Element('{%s}TEI' % TEI_NS)
    apparatus.append(tei)
    #First, add a <teiHeader> element under the TEI element:
    teiHeader = et.Element('{%s}teiHeader' % TEI_NS)
    tei.append(teiHeader)
    #Under this, add a <sourceDesc> element:
    sourceDesc = et.Element('{%s}sourceDesc' % TEI_NS)
    teiHeader.append(sourceDesc)
    #Under this, add a <listWit> element:
    listWit = et.Element('{%s}listWit' % TEI_NS)
    sourceDesc.append(listWit)
    #Under this, add a <witness> element for each witness:
    for witness in witnesses:
        wit = et.Element('{%s}witness' % TEI_NS)
        wit.set('id', witness.ga_id)
        listWit.append(wit)
    #Then, add a <text> element under the TEI element:
    text = et.Element('{%s}text' % TEI_NS)
    text.set('{%s}lang' % XML_NS, 'he')
    tei.append(text)
    #Under this, add a <body> element:
    body = et.Element('body')
    text.append(body)
    #Under this, add a <div> element representing the book:
    book_div = et.Element('div')
    book_div.set('type', 'book')
    body.append(book_div)
    #First, generate an ordered List of verses extant in at least one witness:
    extant_verses = get_extant_verses(witnesses)
    #Get the book index from this List, and use it to populate the attributes of the book div:
    book_tuple = book_to_tuple(extant_verses[0])
    book = book_tuple[0]
    book_ind = 'B%02d' % book
    book_div.set('n', book_ind)
    #Then collate the incipit: 
    incipit_div = collate_incipit(witnesses, params)
    #If it is extant in at least one witnesses, then include it here:
    if incipit_div is not None:
        book_div.append(incipit_div)
    #Then proceed for each verse in the List, keeping a record of the current chapter we're in:
    for verse_index in extant_verses:
        #Get the current book and chapter from this String:
        chapter_tuple = chapter_to_tuple(verse_index)
        book = chapter_tuple[0]
        chapter = chapter_tuple[1]
        #Now search for the chapter div with this index:
        chapter_ind = 'B%02dK%d' % (book, chapter)
        chapter_divs = apparatus.xpath("//div[@type='chapter'][@n='" + chapter_ind + "']")
        chapter_div = None
        #If there isn't one, then create a new one for the chapter:
        if len(chapter_divs) == 0:
            chapter_div = et.Element('div')
            chapter_div.set('type', 'chapter')
            chapter_div.set('n', chapter_ind)
            book_div.append(chapter_div)
        else:
            chapter_div = chapter_divs[0]
        #Now collate the verse, and add it to the chapter div:
        verse_collation = collate_verse(witnesses, verse_index, params)
        chapter_div.append(verse_collation)
    #Finally, collate the explicit:
    explicit_div = collate_explicit(witnesses, params)
    #If it is extant in at least one witnesses, then include it here:
    if explicit_div is not None:
        book_div.append(explicit_div)
    #Then clean up the namespaces for the XML:
    et.cleanup_namespaces(apparatus)
    return apparatus
"""
Given an XML tree representing a generated critical apparatus, adds empty <rdg/> elements for all omissions.
"""
def add_omission_variants(apparatus):
    print('Adding empty <rdg/> elements for omissions...')
    #First, check if the lemma option has been set; if so, there should be at least one <lem/> element in the apparatus:
    lemma = False
    lemma_wit = ''
    lems = apparatus.xpath('//tei:lem', namespaces={'tei': TEI_NS})
    if len(lems) > 0:
        lemma = True
        #Set the lemma witness; it should be the first one listed in the <listWit/> element:
        witnesses = apparatus.xpath('//tei:listWit/tei:witness', namespaces={'tei': TEI_NS})
        lemma_wit = witnesses[0].get('id')
    #Now proceed for each verse:
    verses = apparatus.xpath('//tei:ab', namespaces={'tei': TEI_NS})
    for verse in verses:
        #Get the indices of witnesses extant in this verse, then add them to a Set:
        #WARNING: the TEI standard doesn't encourage specifying a 'wit' attribute for <ab/> elements.
        wit_ids = set(verse.get('wit').split())
        #Now proceed for each point of variation in the verse:
        apps = verse.xpath('./tei:app', namespaces={'tei': TEI_NS})
        for app in apps:
            #Create a Set of extant witness IDs not included in any of the readings:
            covered_wit_ids = set()
            lems = app.xpath('./tei:lem', namespaces={'tei': TEI_NS})
            for lem in lems:
                lem_wit_ids = set(lem.get('wit').split())
                covered_wit_ids = covered_wit_ids.union(lem_wit_ids)
            rdgs = app.xpath('./tei:rdg', namespaces={'tei': TEI_NS})
            for rdg in rdgs:
                rdg_wit_ids = set(rdg.get('wit').split())
                covered_wit_ids = covered_wit_ids.union(rdg_wit_ids)
            #Get the Set of extant witness IDs not covered:
            rem_wit_ids = wit_ids.difference(covered_wit_ids)
            #If this Set is empty, then move on:
            if len(rem_wit_ids) == 0:
                continue
            #Otherwise, add a new <lem/> or <rdg/> element for the omission:
            if lemma and ('#' + lemma_wit) in rem_wit_ids:
                lem = et.Element('{%s}lem' % TEI_NS)
                lem.set('wit', ' '.join(rem_wit_ids))
                app.append(lem)
            else:
                rdg = et.Element('{%s}rdg' % TEI_NS)
                rdg.set('wit', ' '.join(rem_wit_ids))
                app.append(rdg)
    return
"""
Entry point to the script. Parses command-line arguments, reads in witness XML files, collates their texts, and outputs the TEI XML apparatus to the given filename.
"""
def main():
    parser = argparse.ArgumentParser(description='Normalize and collate transcriptions in TEI XML format. The output is an apparatus in TEI XML format.')
    parser.add_argument('witnesses', nargs='+', help='Transcription files in TEI XML format.')
    parser.add_argument('--lemma', action='store_true', help='Treat all readings of the first witness specified as lemma readings (i.e., <lem/> elements).')
    parser.add_argument('--normalize', action='store_true', help='Normalize all text in output.')
    parser.add_argument('--normalize_cantillation', action='store_true', help='Normalize (i.e., ignore) cantillation marks in output.')
    parser.add_argument('--normalize_pointing', action='store_true', help='Normalize (i.e., ignore) pointing in output.')
    parser.add_argument('--normalize_punc', action='store_true', help='Normalize (i.e., ignore) punctuation marks in output.')
    parser.add_argument('--normalize_breaks', action='store_true', help='Normalize (i.e., ignore) section breaks in output.')
    parser.add_argument('--normalize_unclear', action='store_true', help='Treat unclear text as normal in output.')
    parser.add_argument('--normalize_supplied', action='store_true', help='Treat supplied text as normal in output.')
    parser.add_argument('-o', metavar='output', type=str, default='collation.xml', help='Output file address (default: collation.xml).')
    args = parser.parse_args()
    #Parse the I/O arguments:
    witness_filenames = args.witnesses
    output_filename = args.o
    #Parse the normalization options, storing them in a Dictionary:
    params = {}
    params['lemma'] = args.lemma
    if args.normalize:
        params['normalize_cantillation'] = True
        params['normalize_pointing'] = True
        params['normalize_punc'] = True
        params['normalize_breaks'] = True
        params['normalize_unclear'] = True
        params['normalize_supplied'] = True
    else:
        params['normalize_cantillation'] = args.normalize_cantillation
        params['normalize_pointing'] = args.normalize_pointing
        params['normalize_punc'] = args.normalize_punc
        params['normalize_breaks'] = args.normalize_breaks
        params['normalize_unclear'] = args.normalize_unclear
        params['normalize_supplied'] = args.normalize_supplied
    #Now read in the XML of each specified file:
    witnesses = []
    for witness_filename in witness_filenames:
        xml = et.parse(witness_filename)
        witness = Witness(xml)
        witnesses.append(witness)
    #Then perform the collation:
    apparatus = collate(witnesses, params)
    #Add empty <rdg/> elements for omissions:
    add_omission_variants(apparatus)
    #Then write to output:
    et.ElementTree(apparatus).write(output_filename, encoding='utf-8', xml_declaration=True, pretty_print=True)
    return

if __name__=="__main__":
    main()
