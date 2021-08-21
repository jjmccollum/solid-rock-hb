#!/usr/bin/env python3

import argparse
from lxml import etree as et

"""
Class for converting a transcription (including collation data) in TEI XML format to ConTeXt format.
"""
class tei_context_converter:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    
    def __init__(self, **kwargs):
        #Populate a String referring to the book's filename base:
        self.filebase = kwargs['filebase'] if 'filebase' in kwargs else ''
        #Populate a Dictionary of witness sigla, keyed by witness references (e.g., '#WLC'):
        self.wit_sigla = kwargs['wit_sigla'] if 'wit_sigla' in kwargs else {}
        #Populate a Dictionary of book titles, keyed by book numbers (e.g., 'B01'):
        self.book_titles = kwargs['book_titles'] if 'book_titles' in kwargs else {}
        #Populate a Set of ignored apparatus types:
        self.ignored_app_types = kwargs['ignored_app_types'] if 'ignored_app_types' in kwargs else set()
        return
    """
    Converts a <pb/> element in the body to ConTeXt format.
    """
    def format_pb(self, xml):
        context = '\n\\page\n'
        return context
    """
    Converts a <milestone unit="book"/> element in the body to ConTeXt format.
    """
    def format_body_milestone_book(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        book_title = ''
        if n is not None and n in self.book_titles:
            book_title = self.book_titles[n]
            context += '\\startBook[title={%s}]\n' % (book_title)
        #Start the pagecolumns environment:
        context += '\\startpagecolumns[hebrew]\n'
        return context
    """
    Converts a <milestone unit="chapter"/> element in the body to ConTeXt format.
    """
    def format_body_milestone_chapter(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        chapter_title = ''
        if n is not None and 'K' in n:
            chapter_title = n.split('K')[-1]
            context += '\n\\Chapter{%s}' % chapter_title
        return context
    """
    Converts a <milestone unit="verse"/> element in the body to ConTeXt format.
    """
    def format_body_milestone_verse(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        verse_title = ''
        if n is not None and 'V' in n:
            verse_title = n.split('V')[-1]
            context += '\n\\Verse{%s}' % verse_title
        return context
    """
    Converts a <milestone unit="verse"/> element in the body that is the last child of a lemma to ConTeXt format.
    """
    def format_body_milestone_verse_last(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        verse_title = ''
        if n is not None and 'V' in n:
            verse_title = n.split('V')[-1]
            context += '\n\\Verse{%s}\\nospace' % verse_title
        return context
    """
    Converts an <lb type="open"/> element in the body to ConTeXt format.
    """
    def format_body_lb_open(self, xml):
        context = ''
        context += '\\OpenSection '
        return context
    """
    Converts a <space type="closed"/> element in the body to ConTeXt format.
    """
    def format_body_space_closed(self, xml):
        context = ''
        context += '\\ClosedSection '
        return context
    """
    Converts a <w/> element to ConTeXt format.
    """
    def format_w(self, xml):
        context = ''
        context += '%s ' % xml.text
        return context
    """
    Converts a <w/> element that is the last child of an element to ConTeXt format.
    """
    def format_w_last(self, xml):
        context = ''
        context += '%s' % xml.text
        return context
    """
    Recursively converts a <lem/> element to ConTeXt format.
    """
    def format_lem(self, xml):
        context = ''
        #Process the <milestone/>, <lb/>, <space/>, and <w/> elements under this element:
        for child in xml:
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            if raw_tag == 'milestone':
                #Proceed based on the unit of the text division:
                milestone_unit = child.get('unit')
                if milestone_unit == 'chapter':
                    context += self.format_body_milestone_chapter(child)
                elif milestone_unit == 'verse':
                    #Proceed based on whether this verse is the last child of the lemma:
                    if child == xml[-1]:
                        context += self.format_body_milestone_verse_last(child)
                    else:
                        context += self.format_body_milestone_verse(child)
            elif raw_tag == 'lb':
                lb_type = child.get('type')
                if lb_type == 'open':
                    context += self.format_body_lb_open(child)
            elif raw_tag == 'space':
                space_type = child.get('type')
                if space_type == 'closed':
                    context += self.format_body_space_closed(child)
            elif raw_tag == 'w':
                #Proceed based on whether this word is the last child of the lemma:
                if child == xml[-1]:
                    context += self.format_w_last(child)
                else:
                    context += self.format_w(child)
        return context
    """
    Converts a <milestone unit="chapter"/> element in the apparatus to ConTeXt format.
    """
    def format_rdg_milestone_chapter(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        chapter_title = ''
        if n is not None and 'K' in n:
            chapter_title = n.split('K')[-1]
            context += '\\RdgChapter{%s}' % chapter_title
        return context
    """
    Converts a <milestone unit="verse"/> element in the apparatus to ConTeXt format.
    """
    def format_rdg_milestone_verse(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        verse_title = ''
        if n is not None and 'V' in n:
            verse_title = n.split('V')[-1]
            context += '\\RdgVerse{%s}' % verse_title
        return context
    """
    Converts a <milestone unit="verse"/> element in the apparatus that is the last child of a variant reading to ConTeXt format.
    """
    def format_rdg_milestone_verse_last(self, xml):
        context = ''
        #Get the book's title via a lookup in the provided Dictionary:
        n = xml.get('n')
        verse_title = ''
        if n is not None and 'V' in n:
            verse_title = n.split('V')[-1]
            context += '\\RdgVerse{%s}\\nospace' % verse_title
        return context
    """
    Converts an <lb type="open"/> element in the apparatus to ConTeXt format.
    """
    def format_rdg_lb_open(self, xml):
        context = ''
        context += '\\RdgOpenSection '
        return context
    """
    Converts a <space type="closed"/> element in the apparatus to ConTeXt format.
    """
    def format_rdg_space_closed(self, xml):
        context = ''
        context += '\\RdgClosedSection '
        return context
    """
    Recursively converts a <rdg/> element to ConTeXt format.
    """
    def format_rdg(self, xml):
        context = ''
        #Typeset the witness list of this reading:
        wit = xml.get('wit')
        wit_context = ''
        if wit is not None:
            wit_context = wit
            for wit_ref in self.wit_sigla:
                wit_siglum = self.wit_sigla[wit_ref]
                wit_context = wit_context.replace(wit_ref, wit_siglum)
        #Process the <milestone/>, <lb/>, <space/>, and <w/> elements under this element:
        rdg_context = ''
        for child in xml:
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            if raw_tag == 'milestone':
                #Proceed based on the unit of the text division:
                milestone_unit = child.get('unit')
                if milestone_unit == 'chapter':
                    rdg_context += self.format_rdg_milestone_chapter(child)
                elif milestone_unit == 'verse':
                    #Proceed based on whether this verse is the last child of the lemma:
                    if child == xml[-1]:
                        rdg_context += self.format_rdg_milestone_verse_last(child)
                    else:
                        rdg_context += self.format_rdg_milestone_verse(child)
            elif raw_tag == 'lb':
                lb_type = child.get('type')
                if lb_type == 'open':
                    rdg_context += self.format_rdg_lb_open(child)
            elif raw_tag == 'space':
                space_type = child.get('type')
                if space_type == 'closed':
                    rdg_context += self.format_rdg_space_closed(child)
            elif raw_tag == 'w':
                #Proceed based on whether this word is the last child of the reading:
                if child == xml[-1]:
                    rdg_context += self.format_w_last(child)
                else:
                    rdg_context += self.format_w(child)
        context += '\Reading{%s}{%s}' % (rdg_context, wit_context)
        return context
    """
    Recursively converts an <app/> element to ConTeXt format.
    """
    def format_app(self, xml):
        context = ''
        #Get the type of this apparatus:
        app_type = xml.get('type')
        #If this is an ignored type, then typeset its lemma and nothing else:
        if app_type is None or app_type in self.ignored_app_types:
            lem_context = ''
            for child in xml:
                raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
                if raw_tag == 'lem':
                    lem_context += self.format_lem(child)
            context += lem_context + ' '
        #Otherwise, typeset its lemma and variant readings separately:
        else:
            lem_context = ''
            rdg_context = ''
            for child in xml:
                raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
                if raw_tag == 'lem':
                    lem_context += self.format_lem(child)
                elif raw_tag == 'rdg':
                    rdg_context += self.format_rdg(child)
                    if child == xml[1]:
                        rdg_context += '\\PrimaryReadingSep'
                    elif child != xml[-1]:
                        rdg_context += '\\SecondaryReadingSep'
            context += '\\App{%s}{%s}{%s} ' % (app_type, lem_context, rdg_context)
        return context        
    """
    Recursively converts a <body/> element to ConTeXt format.
    """
    def format_body(self, xml):
        context = ''
        #Process the <milestone/>, <lb/>, <space/>, <w/>, and <app/> elements under this element:
        for child in xml:
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            if raw_tag == 'milestone':
                #Proceed based on the unit of the text division:
                milestone_unit = child.get('unit')
                if milestone_unit == 'book':
                    context += self.format_body_milestone_book(child)
                elif milestone_unit == 'chapter':
                    context += self.format_body_milestone_chapter(child)
                elif milestone_unit == 'verse':
                    context += self.format_body_milestone_verse(child)
            elif raw_tag == 'pb':
                context += self.format_pb(child)
            elif raw_tag == 'lb':
                lb_type = child.get('type')
                if lb_type == 'open':
                    context += self.format_body_lb_open(child)
            elif raw_tag == 'space':
                space_type = child.get('type')
                if space_type == 'closed':
                    context += self.format_body_space_closed(child)
            elif raw_tag == 'w':
                #Proceed based on whether this word is the last child of the body:
                if child == xml[-1]:
                    context += self.format_w_last(child)
                else:
                    context += self.format_w(child)
            elif raw_tag == 'app':
                context += self.format_app(child)
        #Close the pagecolumns environment (it will be opened at the 'book' milestone):
        context += '\n\\page[no]\n\\stoppagecolumns\n\\stopBook\n'
        return context
    """
    Recursively converts a <text/> element to ConTeXt format.
    """
    def format_text(self, xml):
        context = ''
        #Open the text environment:
        context += '\\starttext\n'
        context += '%\\startbodymatter %uncomment to trigger appropriate conditional formatting for standalone document\n'
        #Process the <front/>, <body/>, and <back/> elements under this element:
        for child in xml:
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            if raw_tag == 'front':
                pass #this isn't present for our use case, but leaving it here for future reference
            elif raw_tag == 'body':
                context += self.format_body(child)
            elif raw_tag == 'back':
                pass #this isn't present for our use case, but leaving it here for future reference
        #Close the text environment:
        context += '%\\stopbodymatter\n'
        context += '\\stoptext\n'
        return context
    """
    Recursively converts a <TEI/> element to ConTeXt format.
    """
    def format_tei(self, xml):
        context = ''
        context += '\\environment ../sty/sr-style\n'
        context += '\\startcomponent\n'
        context += '\\product ../main/main\n'
        #Process the <text/> element under this element:
        for child in xml:
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            if raw_tag == 'text':
                context += self.format_text(child)
        context += '\\stopcomponent'
        return context
    """
    Recursively converts a transcription (including collation data) in TEI XML format to ConTeXt format.
    """
    def to_context(self, xml):
        context = ''
        #If the input is an XML tree and not an element, then return the serialization of its root element:
        if not et.iselement(xml):
            context += self.format_tei(xml.getroot())
            return context
        return context