#!/usr/bin/env python3

import argparse
from lxml import etree as et

"""
Class representing a polyglossia language with language-specific options.
"""
class polyglossia_language:
    def __init__(self, name, options={}):
        self.name = name
        self.options = options

"""
Class for converting a transcription (including collation data) in TEI XML format to other formats.
"""
class tei_converter:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    """
    Dictionary mapping XML ISO 639-3 language codes to polyglossia's supported languages
    """
    iso_to_polyglossia = {
        'afr': polyglossia_language('afrikaans'),
        'sqi': polyglossia_language('albanian'),
        'amh': polyglossia_language('amharic'),
        'ara': polyglossia_language('arabic'),
        'arz': polyglossia_language('arabic'),
        'apd': polyglossia_language('arabic'),
        'afb': polyglossia_language('arabic'),
        'ayl': polyglossia_language('arabic', {'locale': 'libya'}),
        'arq': polyglossia_language('arabic', {'locale': 'algeria'}),
        'aeb': polyglossia_language('arabic', {'locale': 'tunisia'}),
        'ary': polyglossia_language('arabic', {'locale': 'morocco'}),
        'hye': polyglossia_language('armenian'),
        'hyw': polyglossia_language('armenian', {'variant': 'western'}),
        'ast': polyglossia_language('asturian'),
        'eus': polyglossia_language('basque'),
        'bel': polyglossia_language('belarusian'),
        'ben': polyglossia_language('bengali'),
        'bos': polyglossia_language('bosnian'),
        'bre': polyglossia_language('breton'),
        'bul': polyglossia_language('bulgarian'),
        'cat': polyglossia_language('catalan'),
        'cop': polyglossia_language('coptic'),
        'hrv': polyglossia_language('croatian'),
        'ces': polyglossia_language('czech'),
        'dan': polyglossia_language('danish'),
        'div': polyglossia_language('divehi'),
        'nld': polyglossia_language('dutch'),
        'eng': polyglossia_language('english'),
        'epo': polyglossia_language('esperanto'),
        'est': polyglossia_language('estonian'),
        'fin': polyglossia_language('finnish'),
        'fra': polyglossia_language('french'),
        'fur': polyglossia_language('friulian'),
        'gle': polyglossia_language('gaelic'),
        'gla': polyglossia_language('gaelic', {'variant': 'scottish'}),
        'glg': polyglossia_language('galician'),
        'kat': polyglossia_language('georgian'),
        'deu': polyglossia_language('german'),
        'gsw': polyglossia_language('german', {'variant': 'swiss'}),
        'ell': polyglossia_language('greek'),
        'grc': polyglossia_language('greek', {'variant': 'ancient'}),
        'heb': polyglossia_language('hebrew'),
        'hin': polyglossia_language('hindi'),
        'hun': polyglossia_language('hungarian'),
        'isl': polyglossia_language('icelandic'),
        'ina': polyglossia_language('interlingua'),
        'ita': polyglossia_language('italian'),
        'jpn': polyglossia_language('japanese'),
        'kan': polyglossia_language('kannada'),
        'khm': polyglossia_language('khmer'),
        'kor': polyglossia_language('korean'),
        'kur': polyglossia_language('kurdish'),
        'kmi': polyglossia_language('kurdish'),
        'ckb': polyglossia_language('kurdish', {'variant': 'sorani'}),
        'lao': polyglossia_language('lao'),
        'lat': polyglossia_language('latin'),
        'lav': polyglossia_language('latvian'),
        'lit': polyglossia_language('lithuanian'),
        'mkd': polyglossia_language('macedonian'),
        'msa': polyglossia_language('malay'),
        'zsm': polyglossia_language('malay'),
        'ind': polyglossia_language('malay', {'variant': 'indonesian'}),
        'mal': polyglossia_language('malayalam'),
        'mar': polyglossia_language('marathi'),
        'mon': polyglossia_language('mongolian'),
        'nqo': polyglossia_language('nko'),
        'nor': polyglossia_language('norwegian'),
        'nob': polyglossia_language('norwegian'),
        'nno': polyglossia_language('norwegian', {'variant': 'nynorsk'}),
        'oci': polyglossia_language('occitan'),
        'fas': polyglossia_language('persian'),
        'pms': polyglossia_language('piedmontese'),
        'pol': polyglossia_language('polish'),
        'por': polyglossia_language('portuguese'),
        'ron': polyglossia_language('romanian'),
        'roh': polyglossia_language('romansh'),
        'rus': polyglossia_language('russian'),
        'sme': polyglossia_language('sami'),
        'san': polyglossia_language('sanskrit'),
        'srp': polyglossia_language('serbian'),
        'slk': polyglossia_language('slovak'),
        'slv': polyglossia_language('slovenian'),
        'dsb': polyglossia_language('sorbian'),
        'hsb': polyglossia_language('sorbian', {'variant': 'upper'}),
        'spa': polyglossia_language('spanish'),
        'swe': polyglossia_language('swedish'),
        'syr': polyglossia_language('syriac'),
        'tam': polyglossia_language('tamil'),
        'tel': polyglossia_language('telugu'),
        'tha': polyglossia_language('thai'),
        'bod': polyglossia_language('tibetan'),
        'tur': polyglossia_language('turkish'),
        'tuk': polyglossia_language('turkmen'),
        'ukr': polyglossia_language('ukrainian'),
        'urd': polyglossia_language('urdu'),
        'vie': polyglossia_language('vietnamese'),
        'cym': polyglossia_language('welsh')
    }
    def __init__(self, **kwargs):
        #Populate a String representing a relative path from the output file to its subfiles parent:
        self.subfiles_path = kwargs['subfiles_path'] if 'subfiles_path' in kwargs else None
        #Populate a List of Tuples of substitution patterns for the witness lists of variant readings:
        self.wit_sub_patterns = kwargs['wit_sub_patterns'] if 'wit_sub_patterns' in kwargs else []
        #Populate a Set of ignored apparatus types:
        self.ignored_app_types = kwargs['ignored_app_types'] if 'ignored_app_types' in kwargs else set()
        #Clear all processing variables before we start:
        self.book_title = ''
        return
    """
    Returns a serialization of the book's title from the incipit.
    If there are textual variants in the incipit,
    then only the contents of the lemma reading will be serialized.
    This method is intended to be called from the root of the XML tree.
    """
    def get_book_title(self, xml):
        serialized = ''
        #Get the <body/> element of the XML:
        body = xml.xpath('//tei:body', namespaces={'tei': self.tei_ns})[0]
        #Then find the incipit division marker and the first chapter division marker:
        incipit_divgen = body.xpath('.//tei:divGen[@type=\'incipit\']', namespaces={'tei': self.tei_ns})[0]
        chapter_divgen = body.xpath('.//tei:divGen[@type=\'chapter\']', namespaces={'tei': self.tei_ns})[0]
        #Then get their indices under the body element:
        incipit_ind = body.index(incipit_divgen)
        chapter_ind = body.index(chapter_divgen)
        #Then loop through these elements:
        for i in range(incipit_ind, chapter_ind):
            child = body[i]
            #If this element is a word, then add it to the serialization:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'w':
                if serialized != '':
                    serialized += ' '
                serialized += child.text
            #Otherwise, if it is an apparatus, then serialize the words of the lemma reading:
            elif child.tag.replace('{%s}' % self.tei_ns, '') == 'app':
                lem = child.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
                for w in lem.xpath('.//tei:w', namespaces={'tei': self.tei_ns}):
                    if serialized != '':
                        serialized += ' '
                    serialized += w.text
        return serialized
    """
    Recursively converts a transcription (including collation data) in TEI XML format to LaTeX format.
    """
    def to_latex(self, xml):
        latex = ''
        #If the input is an XML tree and not an element, then return the serialization of its root:
        if not et.iselement(xml):
            #Get the title of the book from the XML:
            self.book_title = self.get_book_title(xml)
            latex += self.to_latex(xml.getroot())
            return latex
        #Otherwise, get the raw tag of this XML element:
        raw_tag = xml.tag.replace('{%s}' % self.tei_ns, '')
        #If this is the root <TEI/> element, then add the LaTeX documentclass tag:
        if raw_tag == 'TEI':
            #If a subfiles path was specified, then use the subfiles document class:
            if self.subfiles_path is not None:
                latex += '\\documentclass[%s]{subfiles}' % self.subfiles_path
            #Otherwise, treat the LaTeX file as a standalone document:
            else:
                latex += '\\documentclass{memoir}'
            #Then recursively process the children of this element:
            latex += '\n'
            for child in xml:
                latex += self.to_latex(child)
            return latex
        #If this is the <text/> element, then add the LaTeX document environment and set the language:
        if raw_tag == 'text':
            language = polyglossia_language('english')
            if xml.get('{%s}lang' % self.xml_ns) is not None:
                iso_code = xml.get('{%s}lang' % self.xml_ns)
                if iso_code in self.iso_to_polyglossia:
                    language = self.iso_to_polyglossia[iso_code]
            latex += '\\begin{document}'
            latex += '\n'
            latex += '\\selectlanguage'
            if len(language.options) > 0:
                latex += '['
                opt_strs = []
                for opt in language.options:
                    opt_strs.append(opt + '=' + language.options[opt])
                latex += ', '.join(opt_strs)
                latex += ']'
            latex += '{' + language.name + '}'
            #Then recursively process the children of this element:
            latex += '\n'
            for child in xml:
                latex += self.to_latex(child)
                latex += '\n'
            #Finally, close off the document:
            latex += '\\end{document}'
            return latex
        #If this is the <body/> element, then recursively process its children, separated by the appropriate spaces:
        if raw_tag == 'body':
            prev_tag = 'body'
            for child in xml:
                current_tag = child.tag.replace('{%s}' % self.tei_ns, '')
                if current_tag in ['space', 'app', 'w'] and prev_tag in ['app', 'w', 'pc']:
                    latex += ' '
                elif prev_tag in ['p', 'lb']:
                    latex += '\\par'
                    latex += '\n'
                elif prev_tag in ['pb']:
                    latex += '\\par'
                    latex += '\n'
                    latex += '\\pagebreak'
                    latex += '\n'
                elif current_tag == 'divGen' and child.get('type') == 'chapter' and prev_tag in ['app', 'w', 'pc']:
                    latex += '\\PreChapterSpace{}'
                elif current_tag == 'divGen' and child.get('type') == 'verse' and prev_tag in ['app', 'w', 'pc']:
                    latex += '\\PreVerseSpace{}'
                latex += self.to_latex(child)
                prev_tag = current_tag
            #Add a final paragraph, and close off the columns environment:
            latex += '\\par'
            latex += '\n'
            latex += '\\end{multicols*}'
            return latex
        #If this is a numbered division marker, then add the appropriate textual division:
        if raw_tag == 'divGen':
            if xml.get('type') is not None and xml.get('n') is not None:
                if xml.get('type') == 'book':
                    #Use the title derived from the incipit for this book:
                    latex += '\\Book{' + self.book_title + '}'
                elif xml.get('type') == 'incipit':
                    latex += '\\thispagestyle{empty}'
                    latex += '\n'
                    latex += '\\Incipit{}'
                elif xml.get('type') == 'explicit':
                    latex += '\\Explicit{}'
                elif xml.get('type') == 'chapter':
                    chapter_n = xml.get('n')
                    #If this is the first chapter division, then add the post-incipit LaTeX macros:
                    if chapter_n.endswith('K1'):
                        latex += '\\cleardoublespace'
                        latex += '\n'
                        latex += '\\RTLmulticolcolumns'
                        latex += '\n'
                        latex += '\\begin{multicols*}{\\ncols}'
                        latex += '\n'
                    if 'K' in chapter_n:
                        chapter_n = chapter_n[chapter_n.index('K') + 1:]
                    latex += '\\Chapter{' + chapter_n + '}'
                elif xml.get('type') == 'verse':
                    verse_n = xml.get('n')
                    if 'V' in verse_n:
                        verse_n = verse_n[verse_n.index('V') + 1:]
                    latex = '\\Verse{' + verse_n + '}'
        #If this is an apparatus, then recursively process its children:
        if raw_tag == 'app':
            #Check the type of variant represented by this apparatus:
            app_type = xml.get('type') if xml.get('type') is not None else 'substitution'
            #If it is not an ignored variation type, then add the appropriate macro in LaTeX and the content of the variant readings:
            if app_type not in self.ignored_app_types:
                if app_type == 'addition':
                    latex += '\\Add{'
                elif app_type == 'omission':
                    latex += '\\OmitBegin{'
                elif app_type == 'transposition':
                    latex += '\\TransBegin{'
                else:
                    latex += '\\SubBegin{'
                #Then process each reading recursively:
                rdg_index = 0
                for rdg in xml.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                    #Don't add any reading separator before the first reading:
                    if rdg_index == 0:
                        latex += ''
                    #Add the primary reading separator before the second reading:
                    elif rdg_index == 1:
                        latex += '\\PrimaryReadingSep{}'
                    #Add a secondary reading separator before every subsequent reading:
                    else:
                        latex += '\\SecondaryReadingSep{}'
                    latex += self.to_latex(rdg)
                    rdg_index += 1
                #Close off the macro:
                latex += '}'
            #Add the lemma text:
            lem = xml.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
            latex += self.to_latex(lem)
            #Then add the appropriate ending macro for the variation, if applicable:
            if app_type not in self.ignored_app_types:
                if app_type == 'addition':
                    latex += ''
                elif app_type == 'omission':
                    latex += '\\OmitEnd{}'
                elif app_type == 'transposition':
                    latex += '\\TransEnd{}'
                else:
                    latex += '\\SubEnd{}'
            return latex
        #If this is a lemma reading element, then recursively process its children, separated by the appropriate spaces:
        if raw_tag == 'lem':
            #If it is empty, then return nothing:
            if len(xml) == 0:
                return ''
            prev_tag = 'lem'
            for lem_child in xml:
                current_tag = lem_child.tag.replace('{%s}' % self.tei_ns, '')
                if current_tag in ['w'] and prev_tag in ['w', 'pc']:
                    latex += ' '
                elif prev_tag in ['p', 'lb']:
                    latex += '\\par'
                    latex += '\n'
                latex += self.to_latex(lem_child)
                prev_tag = current_tag
            return latex
        #If this is a variant reading element, then add the appropriate macro:
        if raw_tag == 'rdg':
            #Add the text of this reading:
            latex += '\\Reading{'
            #If it is empty, then use the omission placeholder to represent it:
            if len(xml) == 0:
                latex += '\Omit{}'
            #Otherwise, process its subelements recursively:
            else:
                prev_tag = 'rdg'
                for rdg_child in xml:
                    current_tag = rdg_child.tag.replace('{%s}' % self.tei_ns, '')
                    if current_tag in ['w'] and prev_tag in ['w', 'pc']:
                        latex += ' '
                    elif prev_tag in ['p', 'lb']:
                        latex += '\\par'
                        latex += '\n'
                    latex += self.to_latex(rdg_child)
                    prev_tag = current_tag
            #Then close the LaTeX macro for the reading:
            latex += '}'
            #Get the String representing this reading's witnesses:
            wit = xml.get('wit')
            #Make the appropriate substitutions for the witnesses:
            for (old, new) in self.wit_sub_patterns:
                wit = wit.replace(old, new)
            witnesses = wit.split()
            #Then add the witness sigla after the reading:
            for witness in witnesses:
                latex += '\\Witness{%s}' % witness
            return latex
        #If this is a line break element, then add the appropriate macro:
        if raw_tag == 'lb':
            #Check the type of this line break, if it has one:
            if xml.get('type') is not None:
                lb_type = xml.get('type')
                if lb_type == 'open':
                    latex += '\\OpenSection{}'
            return latex
        #If this is a space element, then add the appropriate macro:
        if raw_tag == 'space':
            #Check the type of this space, if it has one:
            if xml.get('type') is not None:
                space_type = xml.get('type')
                if space_type == 'closed':
                    latex += '\\ClosedSection{}'
            return latex
        #If this is a word or a punctuation element, then copy its text:
        if raw_tag in ['w', 'pc']:
            latex += xml.text
            return latex
        return latex
