#!/usr/bin/env python3

from lxml import etree as et
from tei_normalizer import tei_normalizer

"""
Class for labeling <app/> elements in a TEI XML collation.
"""
class tei_labeler:
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
    Adds a 'type' attribute to all <app/> elements in the given collation XML file.
    """
    def add_types(self, xml):
        #Proceed for each <app/> element in the XML tree:
        for app in xml.xpath('//tei:app', namespaces={'tei': self.tei_ns}):
            normalizer = tei_normalizer(**{'a': set(['cantillation', 'pointing', 'extraordinaire']), 'p': set(), 'r': None, 't': set()})
            #First, serialize the primary reading at its current level of normalization:
            primary_rdg = app.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns})[0]
            primary_rdg_tokens = []
            for el in primary_rdg:
                if el.text is None:
                    primary_rdg_tokens.append(el.tag)
                else:
                    primary_rdg_tokens.append(el.text)
            primary_rdg_serialization = ' '.join(primary_rdg_tokens)
            #Then get corresponding serializations of the remaining variant readings:
            variant_rdg_serializations = []
            for rdg in app.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns})[1:]:
                rdg_tokens = []
                for el in rdg:
                    if el.text is None:
                        rdg_tokens.append(el.tag)
                    else:
                        rdg_tokens.append(el.text)
                rdg_serialization = ' '.join(rdg_tokens)
                variant_rdg_serializations.append(rdg_serialization)
            #If all readings are equal in their fully-normalized form, then the variant is a vocalic one:
            is_vocalic = True
            for rdg_serialization in variant_rdg_serializations:
                if normalizer.format_text(rdg_serialization) != normalizer.format_text(primary_rdg_serialization):
                    is_vocalic = False
                    break
            if is_vocalic:
                app.set('type', 'vocalic')
                continue
            #Otherwise, if both readings stripped of plene letters are equal, then the variant is orthographic:
            is_orthographic = True
            for rdg_serialization in variant_rdg_serializations:
                if normalizer.format_text(normalizer.strip_plene(rdg_serialization)) != normalizer.format_text(normalizer.strip_plene(primary_rdg_serialization)):
                    is_orthographic = False
                    break
            if is_orthographic:
                app.set('type', 'orthographic')
                continue
            #Otherwise, if all readings in fully-normalized form are equal up to order, then the variant is a transposition:
            is_transposition = True
            for rdg_serialization in variant_rdg_serializations:
                if set(normalizer.format_text(rdg_serialization).split()) != set(normalizer.format_text(primary_rdg_serialization).split()):
                    is_transposition = False
                    break
            if is_transposition:
                app.set('type', 'transposition')
                continue
            #Otherwise, check if the variant is an addition or an omission relative to the primary reading:
            if len(primary_rdg_serialization.split()) == 0:
                is_addition = True
                for rdg_serialization in variant_rdg_serializations:
                    if len(rdg_serialization.split()) == 0:
                        is_addition = False
                        break
                if is_addition:
                    app.set('type', 'addition')
                    continue
            else:
                is_omission = True
                for rdg_serialization in variant_rdg_serializations:
                    if len(rdg_serialization.split()) > 0:
                        is_omission = False
                        break
                if is_omission:
                    app.set('type', 'omission')
                    continue
            #Otherwise, the variant is a substitution:
            app.set('type', 'substitution')
        return
    """
    Recursively adds 'n' attributes to all <app/> elements in the given collation XML file using their lemma readings.
    """
    def add_indices(self, xml):
        #If the input is the tree itself, then recurse on its root:
        if not et.iselement(xml):
            self.add_indices(xml.getroot())
            return
        #Otherwise, proceed according to the element's tag:
        raw_tag = xml.tag.replace('{%s}' % self.tei_ns, '')
        #If it is a textual division, then add the index of its division type to the Dictionary and reset the indices of any lower-level divisions and words:
        if raw_tag == 'divGen':
            if xml.get('type') is not None:
                div_type = xml.get('type')
                div_n = xml.get('n') if xml.get('n') is not None else ''
                #If the division's index contains its number in addition to previous divisions' numbers, then just get the index for this division:
                if div_type in ['incipit', 'explicit']:
                    div_n = ''
                elif self.div_abbreviations[div_type] in div_n:
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
            #If no word has been encountered yet (i.e., if the first variant is at the very beginning of the text),
            #then set it now:
            if 'w' not in self.div_indices:
                self.div_hierarchy.append('w')
                self.div_indices['w'] = '0'
            #Get the lemma reading:
            lem = xml.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
            #Save the current indices:
            app_start_indices = self.div_indices.copy()
            #Index the children of the lemma reading:
            for child in lem:
                self.add_indices(child)
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
            self.add_indices(child)
        return
    """
    Labels to all <app/> elements in the given XML tree, adding 'type' and 'n' attributes to each one.
    """
    def label(self, xml):
        self.add_types(xml)
        self.add_indices(xml)
        return
            
