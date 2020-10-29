#!/usr/bin/env python3

from lxml import etree as et

"""
Class for indexing <app/> elements in a TEI XML collation.
"""
class tei_indexer:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    """
    Dictionary of abbreviations for textual division types
    """
    div_abbreviations = {
        'book': 'B',
        'incipit': 'incipit',
        'explicit': 'explicit',
        'chapter': 'K',
        'verse': 'V',
        'w': 'U'
    }
    def __init__(self, **params):
        self.div_hierarchy = [] #this List should be populated in top-down order
        self.div_indices = {} #contains the latest div and word indices
        return
    """
    Recursively indexes all <app/> elements in the given collation XML file using its lemma readings.
    """
    def index(self, xml):
        #If the input is the tree itself, then recurse on its root:
        if not et.iselement(xml):
            self.index(xml.getroot())
            return
        #Otherwise, proceed according to the element's tag:
        raw_tag = xml.tag.replace('{%s}' % self.tei_ns, '')
        #If it is a textual division, then add the index of its division unit to the Dictionary and reset the indices of any lower-level divisions and words:
        if raw_tag == 'milestone':
            if xml.get('unit') is not None:
                div_type = xml.get('unit')
                div_n = xml.get('n') if xml.get('n') is not None else ''
                #If the division's index contains its number in addition to previous divisions' numbers, then just get the index for this division:
                if self.div_abbreviations[div_type] in div_n:
                    div_n = div_n[div_n.index(self.div_abbreviations[div_type]) + 1:]
                #If the division is an incipit or explicit, then temporarily replace the 'chapter' entry with the appropriate division name in the hierarchy List:
                if div_type in ['incipit', 'explicit']:
                    if 'chapter' in self.div_hierarchy:
                        self.div_hierarchy[self.div_hierarchy.index('chapter')] = div_type
                    else:
                        self.div_hierarchy.append(div_type)
                #If the division is a chapter, then replace any 'incipit' or 'explicit' entries in the hierarchy List with 'chapter':
                if div_type == 'chapter':
                    if 'incipit' in self.div_hierarchy:
                        self.div_hierarchy[self.div_hierarchy.index('incipit')] = div_type
                    elif 'explicit' in self.div_hierarchy:
                        self.div_hierarchy[self.div_hierarchy.index('explicit')] = div_type
                #If this type of division has not been encountered yet, then add it to the hierarchy List:
                if div_type not in self.div_hierarchy:
                    self.div_hierarchy.append(div_type)
                #Add this division's index to the Dictionary:
                self.div_indices[div_type] = div_n
                #Then reset the lower-level indices:
                for other_div_type in self.div_hierarchy[self.div_hierarchy.index(div_type) + 1:]:
                    self.div_indices[other_div_type] = '0'
            return
        #If it is a word, then add its index to the Dictionary:
        if raw_tag == 'w':
            if raw_tag not in self.div_indices:
                self.div_hierarchy.append(raw_tag)
                self.div_indices[raw_tag] = '0'
            self.div_indices[raw_tag] = str(int(self.div_indices[raw_tag]) + 2)
            return
        #Otherwise, if it is an apparatus, then add an index to it:
        if raw_tag == 'app':
            #Check if any reading in this apparatus contains any words:
            is_paratextual = len(xml.xpath('.//tei:w', namespaces={'tei': self.tei_ns})) == 0
            #Get the lemma reading:
            lem = xml.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
            #Save the current indices:
            app_start_indices = self.div_indices.copy()
            #Index the children of the lemma reading:
            for child in lem:
                self.index(child)
            #Save the updated indices:
            app_end_indices = self.div_indices.copy()
            #If the start and end indices are the same, then either the apparatus covers a paratextual issue, 
            #or the lemma reading is empty:
            if app_start_indices == app_end_indices:
                #If the apparatus contains at least one word, then the lemma reading is an omission;
                #otherwise, use the starting indices as they are:
                if len(xml.xpath('.//tei:w', namespaces={'tei': self.tei_ns})) > 0:
                    app_start_indices['w'] = str(int(app_start_indices['w']) + 1)
                app_n = ''
                for div_type in self.div_hierarchy:
                    #If we're in an incipit or explicit, then ignore the verse number:
                    if ('incipit' in self.div_hierarchy or 'explicit' in self.div_hierarchy) and div_type == 'verse':
                        continue
                    app_n += self.div_abbreviations[div_type] + app_start_indices[div_type]
                xml.set('n', app_n)
            #Otherwise, the lemma contains at least one word: move the starting index to the index of this word:
            else:
                app_start_indices['w'] = str(int(app_start_indices['w']) + 2)
                #If the start and end indices now match, then the lemma reading consists of one word:
                if app_start_indices == app_end_indices:
                    app_n = ''
                    for div_type in self.div_hierarchy:
                        #If we're in an incipit or explicit, then ignore the verse number:
                        if ('incipit' in self.div_hierarchy or 'explicit' in self.div_hierarchy) and div_type == 'verse':
                            continue
                        app_n += self.div_abbreviations[div_type] + app_start_indices[div_type]
                    xml.set('n', app_n)
                #Otherwise, determine the first textual division level where the start index and the end index differ:
                else:
                    difference_level = None
                    for div_type in self.div_hierarchy:
                        if app_start_indices[div_type] != app_end_indices[div_type]:
                            difference_level = div_type
                            break
                    #Add a range marker after the start index and add only the part of the end index that isn't redundant:
                    app_n = ''
                    for div_type in self.div_hierarchy:
                        #If we're in an incipit or explicit, then ignore the verse number:
                        if ('incipit' in self.div_hierarchy or 'explicit' in self.div_hierarchy) and div_type == 'verse':
                            continue
                        app_n += self.div_abbreviations[div_type] + app_start_indices[div_type]
                    app_n += '-'
                    for div_type in self.div_hierarchy[self.div_hierarchy.index(difference_level):]:
                        #If we're in an incipit or explicit, then ignore the verse number:
                        if ('incipit' in self.div_hierarchy or 'explicit' in self.div_hierarchy) and div_type == 'verse':
                            continue
                        app_n += self.div_abbreviations[div_type] + app_end_indices[div_type]
                    xml.set('n', app_n)
            return
        #For all other elements, process their children recursively:
        for child in xml:
            self.index(child)
        return
