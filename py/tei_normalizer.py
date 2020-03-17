#!/usr/bin/env python3

from lxml import etree as et
import unicodedata as ud
import re

"""
Class for normalizing TEI XML transcriptions of Hebrew text.
"""
class tei_normalizer:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    """
    Dictionary of regular expressions, keyed by accentuation type:
    """
    accentuatation_res = {
        'cantillation': re.compile('[\u0591-\u05AF\u05BD\u200C-\u200D]'), #meteg (\u05BD) is described as a point in its Unicode name, but it's functionally an accent #TODO: should zero-width joiners and non-joiners (\u200C-\u200D) belong to the pointing accentuation set?
        'pointing': re.compile('[\u05B0-\u05BC\u05BF\u05C1-\u05C2\u05C7]'),
        'extraordinaire': re.compile('[\u05C4-\u05C5]')
    }
    """
    Whitespace characters to facilitate pretty-printing, keyed by element tag:
    """
    pretty_print_whitespace = {
        'pb': '',
        'cb': '',
        'lb': '',
        'p': '',
        'space': '',
        'app': '',
        'lem': '',
        'rdg': '',
        'w': '',
        'pc': ''
    }
    def __init__(self, **params):
        self.ignored_accent_set = params['a'] if 'a' in params else set()
        self.ignored_punc_set = params['p'] if 'p' in params else set()
        self.preferred_rdg_type = params['r'] if 'r' in params else None
        self.ignored_tag_set = params['t'] if 't' in params else set()
    """
    Given a String, conditionally strips different types of accentuation from it according to the parameters of this normalizer.
    """
    def format_text(self, s):
        s = ud.normalize('NFKD', s) #decompose any precomposed Unicode characters
        for accentuation_type in self.ignored_accent_set:
            regex = self.accentuatation_res[accentuation_type]
            s = re.sub(regex, '', s)
        s = ud.normalize('NFC', s) #re-compose the decomposed Unicode characters
        return s
    """
    Given a String (assumed to have pointing), returns it with any plene / male letters replaced with their defective vocalizations.
    """
    def strip_plene(self, s):
        #First, decompose any precomposed Unicode characters:
        s = ud.normalize('NFKD', s) 
        #Then loop through the characters, grouping points with the appropriate characters:
        letters_re = re.compile('[\u05D0-\u05EA]')
        vowels_re = self.accentuatation_res['pointing']
        letters_with_pointing = []
        letter_with_pointing = ''
        new_letter = False
        for c in s:
            #Skip any characters that are not relevant to this process:
            if c != ' ' and letters_re.match(c) is None and vowels_re.match(c) is None:
                continue
            #If the current character is a space or a letter, then add all characters in the queue as a new letter with pointing:
            if c == ' ' or letters_re.match(c):
                letters_with_pointing.append(letter_with_pointing)
                letter_with_pointing = ''
            #Add the current character to the queue:
            letter_with_pointing += c
        #Add the remaining contents of the queue as a new letter with pointing:
        letters_with_pointing.append(letter_with_pointing)
        #Remove the empty first entry:
        letters_with_pointing = letters_with_pointing[1:]
        #Loop through this List and make the appropriate replacements:
        current_letter_with_pointing = ''
        prev_letter_with_pointing = ''
        for i in range(len(letters_with_pointing)):
            #Get the letter at this index:
            current_letter_with_pointing = letters_with_pointing[i]
            #If this is a space, then leave it unchanged:
            if current_letter_with_pointing == ' ':
                pass
            #If this is the first letter in a word, then leave it unchanged:
            elif i == 0 or prev_letter_with_pointing == ' ':
                pass
            #If this is the last letter in a word, then leave it unchanged:
            elif i == len(letters_with_pointing) - 1 or letters_with_pointing[i+1] == ' ':
                pass
            #If the current letter is an unpointed alef, then drop it:
            elif current_letter_with_pointing == '\u05D0':
                letters_with_pointing[i] = ''
            #If the current letter is an unpointed vav preceded by an unpointed alef and this digraph isn't at the start of the word, 
            #then drop both letters and add a holam to the letter before the digraph, if it isn't there already:
            elif current_letter_with_pointing == '\u05D5' and prev_letter_with_pointing == '\u05D0' and i > 1 and letters_with_pointing[i-2] != ' ':
                letters_with_pointing[i] = ''
                letters_with_pointing[i-1] = ''
                if '\u05B9' not in letters_with_pointing[i-2]:
                    letters_with_pointing[i-2] += '\u05B9'
            #If the current letter is a vav with a (male) holam, then drop it and add a holam to the previous letter:
            elif current_letter_with_pointing == '\u05D5\u05B9':
                letters_with_pointing[i] = ''
                letters_with_pointing[i-1] += '\u05B9'
            #If the current letter is a vav with a dagesh and no other pointing, then drop it and add a qubuts to the previous letter:
            elif current_letter_with_pointing == '\u05D5\u05BC':
                letters_with_pointing[i] = ''
                letters_with_pointing[i-1] += '\u05BB'
            #If the current letter is an unpointed yodh and the previous letter is pointed with a hiriq, tsere, or segol, then drop this letter:
            elif current_letter_with_pointing == '\u05D9' and ('\u05B4' in prev_letter_with_pointing or '\u05B5' in prev_letter_with_pointing or '\u05B6' in prev_letter_with_pointing):
                letters_with_pointing[i] = ''
            #If the current letter is a yodh with a sheva and the previous letter is pointed with a hiriq, tsere, or segol, then drop this letter:
            elif current_letter_with_pointing == '\u05D9\u05B0' and ('\u05B4' in prev_letter_with_pointing or '\u05B5' in prev_letter_with_pointing or '\u05B6' in prev_letter_with_pointing):
                letters_with_pointing[i] = ''
            #Then update the previous letter and move on:
            prev_letter_with_pointing = current_letter_with_pointing
        #Then join the resulting characters into a single String:
        s = ''.join(letters_with_pointing)
        #Then re-compose the decomposed Unicode characters:
        s = ud.normalize('NFC', s)
        return s
    """
    Given an XML element, adds the appropriate whitespace character to its tail to facilitate pretty-printing.
    """
    def add_pretty_print_tail(self, xml):
        raw_tag = xml.tag.replace('{%s}' % self.tei_ns, '')
        if raw_tag in self.pretty_print_whitespace:
            whitespace = self.pretty_print_whitespace[raw_tag]
            xml.tail = whitespace if xml.text is None else xml.tail
        return
    """
    Given a TEI <app/> XML element, returns a List of the children of the <rdg/> element whose type matches the preferred reading type of this normalizer.
    """
    def get_preferred_rdg_elements(self, xml):
        rdg_children = []
        rdg = xml.xpath('tei:rdg[@type=\'%s\']' % self.preferred_rdg_type, namespaces={'tei': self.tei_ns})[0]
        for child in rdg.getchildren():
            rdg_children.append(child)
        return rdg_children
    """
    Recursively normalizes an input XML element and its children according to the parameters of this normalizer.
    """
    def normalize(self, xml):
        out_xml = None
        #If this is a tree, then normalize the root:
        if not et.iselement(xml):
            out_xml = self.normalize(xml.getroot())
            return et.ElementTree(out_xml)
        #Get the element tag:
        tag = xml.tag
        #Convert div and ab elements to standalone divGen elements:
        if tag.replace('{%s}' % self.tei_ns, '') in ['div', 'ab']:
            tag = '{%s}divGen' % self.tei_ns
        #If this element has no parent, then add the namespace map to the normalized element:
        if xml.getparent() is None:
            out_xml = et.Element(tag, nsmap={None: self.tei_ns, 'xml': self.xml_ns})
        #Otherwise, generate the XML element without the namespace map:
        else:
            out_xml = et.Element(tag)
        #If the original element was a verse division, then add an attribute indicating this:
        if xml.tag.replace('{%s}' % self.tei_ns, '') == 'ab':
            out_xml.set('type', 'verse')
        #Copy all attributes to the output element:
        for attr in xml.attrib:
            out_xml.set(attr, xml.get(attr))
        #Conditionally format the text:
        if xml.text is not None:
            out_xml.text = self.format_text(xml.text)
        #Then recursively normalize all child elements:
        for child in xml.getchildren():
            #Skip elements whose tags are in the ignored tag set:
            if child.tag.replace('{%s}' % self.tei_ns, '') in self.ignored_tag_set:
                #But conditionally format their tails, if they has one: 
                if child.tail is not None:
                    tail = self.format_text(child.tail)
                    #Append this tail to the last child of the output element,
                    #or to the text of the output element if it has no children:
                    if len(out_xml.getchildren()) > 0:
                        last = out_xml.getchildren()[-1]
                        last.tail = last.tail + tail if last.tail is not None else tail
                    else:
                        out_xml.text = out_xml.text + tail if out_xml.text is not None else tail
                continue
            #Skip punctuation elements whose text values are in the ignored punctuation set:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'pc':
                if child.text is not None and child.text in self.ignored_punc_set:
                    #But conditionally format their tails, if they has one: 
                    if child.tail is not None:
                        tail = self.format_text(child.tail)
                        #Append this tail to the last child of the output element,
                        #or to the text of the output element if it has no children:
                        if len(out_xml.getchildren()) > 0:
                            last = out_xml.getchildren()[-1]
                            last.tail = last.tail + tail if last.tail is not None else tail
                        else:
                            out_xml.text = out_xml.text + tail if out_xml.text is not None else tail
                    continue
            out_child = self.normalize(child)
            #If the child is an app instance, then process it conditionally:
            if out_child.tag.replace('{%s}' % self.tei_ns, '') == 'app':
                if self.preferred_rdg_type is not None:
                    #Just get the ketiv reading's child elements, and add them instead:
                    preferred_rdg_elements = self.get_preferred_rdg_elements(out_child)
                    for out_grandchild in preferred_rdg_elements:
                        out_xml.append(out_grandchild)
                else:
                    out_xml.append(out_child)
            #Otherwise, if the child has been converted to a divGen instance, then make its children its siblings:
            elif out_child.tag.replace('{%s}' % self.tei_ns, '') == 'divGen':
                out_grandchildren = out_child.getchildren()
                for out_grandchild in out_grandchildren:
                    out_child.remove(out_grandchild)
                out_child.text = None #Remove whitespace to ensure that the element's opening and closing tags are merged
                out_xml.append(out_child)
                for out_grandchild in out_grandchildren:
                    out_xml.append(out_grandchild)
            #Otherwise, append the child normally:
            else:
                out_xml.append(out_child)
            #Conditionally format the tail of the child element:
            if child.tail is not None:
                out_child.tail = self.format_text(child.tail)
            else:
                self.add_pretty_print_tail(out_child)
        return out_xml
