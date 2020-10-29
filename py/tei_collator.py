#!/usr/bin/env python3

from lxml import etree as et
from copy import deepcopy
import json
import collatex as cx
from tei_normalizer import tei_normalizer
from tei_segmenter import tei_segmenter

"""
Class for collating TEI XML transcriptions of Hebrew text.
"""
class tei_collator:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    """
    Data structures for witnesses
    """
    lemma = None #the ID of the witness representing the lemma
    lemma_xml = None #the (unnormalized) TEI XML transcription of the lemma text
    witnesses = [] #List of witness IDs, in the order they were added
    primary_to_secondary = {} #map from primary witness IDs to a List of their corresponding secondary witness IDs
    tokens_by_witness = {} #map from witness IDs to Dictionaries of token Lists keyed by textual division numbers
    collation_xml = None #the normalized TEI XML collation of all witnesses
    def __init__(self, **params):
        self.level = params['l'] if 'l' in params else 'verse' #textual division level (e.g., book, chapter, verse) to group tokens for collation
        self.ignored_accent_set = params['a'] if 'a' in params else set()
        self.ignored_tag_set = params['t'] if 't' in params else set()
    """
    Given an unnormalized TEI XML representing a single witness, returns a String representing its name.
    """
    def get_witness_name(self, xml):
        #The name is located in the second <title/> element:
        title = xml.xpath('//tei:title', namespaces={'tei': self.tei_ns})[1]
        wit_n = title.get('n') if title.get('n') is not None else title.text
        return wit_n
    """
    Given an unnormalized TEI XML element representing a single witness, returns a List of all of the types of its <rdg/> elements.
    """
    def get_rdg_types(self, xml):
        rdg_types = []
        distinct_rdg_types = set()
        rdgs = xml.xpath('//tei:rdg', namespaces={'tei': self.tei_ns})
        for rdg in rdgs:
            #Skip any readings that do not have a type:
            if rdg.get('type') is None:
                continue
            #Otherwise, add its type to the List if it hasn't been encountered yet:
            rdg_type = rdg.get('type')
            if rdg_type not in distinct_rdg_types:
                rdg_types.append(rdg_type)
                distinct_rdg_types.add(rdg_type)
        return rdg_types
    """
    Given a normalized XML tree with formatted text and a normalized XML tree with unformatted text,
    returns a Dictionary, keyed by div index, of a List of tokens representing each element as it is found in each tree.
    """
    def get_tokens_by_div(self, t_xml, n_xml):
        tokens_by_div = {}
        #Iterate through every child of the <body/> element (normalization should flatten these to the same level):
        t_body = t_xml.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        t_elements = t_body.getchildren()
        n_body = n_xml.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
        n_elements = n_body.getchildren()
        div_n = None
        tokens = []
        for i in range(len(t_elements)):
            t_element = t_elements[i]
            n_element = n_elements[i]
            #Add the latest list of tokens to the Dictionary and update the current div index if this is a divider at the appropriate level:
            if t_element.tag.replace('{%s}' % self.tei_ns, '') == 'milestone':
                if t_element.get('unit') is not None and t_element.get('unit') in [self.level, 'incipit' ,'explicit'] and t_element.get('n') is not None:
                    if div_n is not None:
                        tokens_by_div[div_n] = tokens.copy()
                        tokens = []
                    div_n = t_element.get('n')
            token = {}
            #For the formatted part of the token, use the serialization of the XML element (so it can be reconstructed easily later):
            token['t'] = et.tostring(t_element, encoding='unicode').strip() #strip surrounding whitespace
            #For the normalized part of the token, use the text of the XML element is it has any; otherwise, use its tag:
            if n_element.text is not None:
                token['n'] = n_element.text
            else:
                token['n'] = n_element.tag
            tokens.append(token)
        #Add the tokens for the last div:
        tokens_by_div[div_n] = tokens.copy()
        return tokens_by_div
    """
    Given the address of a TEI XML transcription file, 
    creates a normalized XML tree for each distinct reading type found in the file
    and adds it to this collator's witness data structures.
    """
    def read_witness(self, file_addr):
        #Parse the XML tree from the file:
        input_xml = et.parse(file_addr)
        #Get the primary witness's ID:
        primary_wit_id = self.get_witness_name(input_xml)
        #Get its reading types:
        rdg_types = self.get_rdg_types(input_xml)
        #If there are no secondary reading types, then treat the witness as primary and remove any <app/> elements it might have in normalization:
        if len(rdg_types) == 0:
            self.witnesses.append(primary_wit_id)
            #If the lemma witness has not been set, then set it to this witness:
            if self.lemma is None:
                self.lemma = primary_wit_id
                self.lemma_xml = input_xml
            #Then create normalized XML trees from which to extract tokens:
            t_ignored_accent_set = self.ignored_accent_set.copy()
            t_ignored_tag_set = self.ignored_tag_set.copy()
            t_normalizer = tei_normalizer(**{'a': t_ignored_accent_set, 'p': set(), 'r': None, 't': t_ignored_tag_set})
            t_xml = t_normalizer.normalize(input_xml)
            n_ignored_accent_set = set(['cantillation', 'pointing', 'extraordinaire'])
            n_ignored_tag_set = self.ignored_tag_set.copy()
            n_normalizer = tei_normalizer(**{'a': n_ignored_accent_set, 'p': set(), 'r': None, 't': n_ignored_tag_set})
            n_xml = n_normalizer.normalize(input_xml)
            #Get a List of tokens for this witness, and add it to this collator's Dictionary:
            tokens_by_div = self.get_tokens_by_div(t_xml, n_xml)
            self.tokens_by_witness[primary_wit_id] = tokens_by_div
        #Otherwise, get a separate XML tree for each reading type:
        else:
            self.primary_to_secondary[primary_wit_id] = []
            for rdg_type in rdg_types:
                #If the lemma witness has not been set, then set it to this witness:
                if self.lemma is None:
                    self.lemma = primary_wit_id
                    lemma_normalizer = tei_normalizer(**{'a': set(), 'p': set(), 'r': rdg_type, 't': set()})
                    self.lemma_xml = lemma_normalizer.normalize(input_xml)
                #Create a secondary witness for each reading type, and add it to the primary witness's List:
                secondary_wit_id = primary_wit_id + '-' + rdg_type
                self.witnesses.append(secondary_wit_id)
                self.primary_to_secondary[primary_wit_id].append(secondary_wit_id)
                #Then create normalized XML trees from which to extract tokens:
                t_ignored_accent_set = self.ignored_accent_set.copy()
                t_preferred_rdg_type = rdg_type
                t_ignored_tag_set = self.ignored_tag_set.copy()
                t_normalizer = tei_normalizer(**{'a': t_ignored_accent_set, 'p': set(), 'r': t_preferred_rdg_type, 't': t_ignored_tag_set})
                t_xml = t_normalizer.normalize(input_xml)
                n_ignored_accent_set = set(['cantillation', 'pointing', 'extraordinaire'])
                n_preferred_rdg_type = rdg_type
                n_ignored_tag_set = self.ignored_tag_set.copy()
                n_normalizer = tei_normalizer(**{'a': n_ignored_accent_set, 'p': set(), 'r': n_preferred_rdg_type, 't': n_ignored_tag_set})
                n_xml = n_normalizer.normalize(input_xml)
                #Get a List of tokens for this witness, and add it to this collator's Dictionary:
                tokens_by_div = self.get_tokens_by_div(t_xml, n_xml)
                self.tokens_by_witness[secondary_wit_id] = tokens_by_div
        return
    """
    Collates all added witnesses using CollateX.
    The collation is done at this collator's specified level of textual division, for performance purposes,
    and the collated chunks are then added to this collator's full TEI XML collation tree.
    After this step, additional <rdg/> elements are added to represent omissions in units where witnesses are extant, but don't have a reading.
    Note that only textual divisions found in the lemma are collated.
    """
    def collate(self):
        #Initialize this collator's XML tree as an empty TEI element:
        self.collation_xml = et.Element('{%s}TEI' % self.tei_ns, nsmap={None: self.tei_ns, 'xml': self.xml_ns})
        #Perform the collation in "chunks" at the specified level of textual division:
        divs = self.lemma_xml.xpath('//tei:milestone[@unit=\'%s\' or @unit=\'incipit\' or @unit=\'explicit\']' % self.level, namespaces={'tei': self.tei_ns})
        for div in divs:
            #Skip any textual divisions without indices:
            if div.get('n') is None:
                continue
            div_n = div.get('n')
            collation = {}
            witnesses = []
            for witness, tokens_by_div in self.tokens_by_witness.items():
                #If this witness is extant at this division, then add its tokens to the collation:
                if div_n in tokens_by_div:
                    tokens = tokens_by_div[div_n]
                    witnesses.append({'id': witness, 'tokens': tokens})
            collation['witnesses'] = witnesses
            #Convert the populated Dictionary to a JSON Object:
            collation = json.loads(json.dumps(collation))
            #Now use CollateX to collate:
            cx_out = cx.collate(collation, segmentation=False, output='tei')
            #Unescape the escaped < and > characters:
            cx_out = cx_out.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            #Parse the output XML:
            apparatus = et.XML(cx_out)
            #Then add each of its children to this collator's collation XML:
            for child in apparatus.getchildren():
                self.collation_xml.append(child)
        #Next, add empty <rdg/> elements to all apparatus elements where any witness is extant, but omits:
        extant_witnesses = []
        for child in self.collation_xml.getchildren():
            #If this element is a textual division at the specified grouping level, then populate a List of witnesses extant at it:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'milestone' and child.get('unit') is not None and child.get('unit') in [self.level, 'incipit', 'explicit'] and child.get('n') is not None:
                div_n = child.get('n')
                extant_witnesses = []
                for witness in self.witnesses:
                    extant_divs = self.tokens_by_witness[witness]
                    if div_n in extant_divs:
                        extant_witnesses.append(witness)
                continue
            #If this element is an apparatus, then check if all extant witnesses are covered by its readings:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'app':
                uncovered_witnesses = set(extant_witnesses)
                for rdg in child.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                    for wit_ref in rdg.get('wit').split():
                        witness = wit_ref.replace('#', '')
                        uncovered_witnesses.remove(witness)
                if len(uncovered_witnesses) == 0:
                    continue
                #If not all witnesses are covered, then add an empty reading supported by them:
                omit_rdg = et.Element('{%s}rdg' % self.tei_ns)
                omit_rdg_wits = []
                for witness in self.witnesses:
                    if witness in uncovered_witnesses:
                        wit_ref = '#' + witness
                        omit_rdg_wits.append(wit_ref)
                omit_rdg.set('wit', ' '.join(omit_rdg_wits))
                #If the lemma witness supports the omission, then make it the first child of the apparatus:
                lemma_ref = '#' + self.lemma
                if lemma_ref in omit_rdg_wits:
                    child[0].addprevious(omit_rdg)
                #Otherwise, make the omission the last child:
                else:
                    child.append(omit_rdg)
        return
    """
    Updates the lemma witness's XML tree, adding <app/> elements containing collation data at the appropriate location of its <w/> elements.
    """
    def augment_lemma(self):
        #Get the lemma XML tree's <sourceDesc/> element:
        sourceDesc = self.lemma_xml.xpath('//tei:sourceDesc', namespaces={'tei': self.tei_ns})[0]
        #Add a witness list under it:
        listWit = et.Element('{%s}listWit' % self.tei_ns)
        sourceDesc.append(listWit)
        #Under this, add a <witness/> element for each witness:
        for wit in self.witnesses:
            witness = et.Element('{%s}witness' % self.tei_ns)
            witness.set('{%s}id' % self.xml_ns, wit)
            listWit.append(witness)
        #Segment the lemma, grouping any elements in this collator's ignored tag set with the appropriate substantive elements:
        segmenter = tei_segmenter(t=self.ignored_tag_set)
        segmenter.segment(self.lemma_xml)
        #Next, loop through the elements in the collation, maintaining a Dictionary of substantive element indices:
        substantive_indices = {}
        segment_type = '' #the tag of the substantive element in the current segment:
        segment_n = '' #the index of the substantive element in the current segment:
        for child in self.collation_xml.getchildren():
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            #If the element is an apparatus, then add it to the lemma:
            if raw_tag == 'app':
                #Add a copy of this apparatus after the segment corresponding to the last substantive element encountered or the latest apparatus added:
                app = deepcopy(child)
                if segment_type == 'app':
                    last_app = self.lemma_xml.xpath('//tei:app', namespaces={'tei': self.tei_ns})[-1]
                    last_app.addnext(app)
                else:
                    last_seg = self.lemma_xml.xpath('//tei:seg[@type=\'%s\' and @n=\'%s\']' % (segment_type, segment_n), namespaces={'tei': self.tei_ns})[0]
                    last_seg.addnext(app)
                #Add the tag and index of this apparatus to the Dictionary:
                if raw_tag not in substantive_indices:
                    substantive_indices[raw_tag] = 0
                else:
                    substantive_indices[raw_tag] += 1
                segment_type = raw_tag
                segment_n = str(substantive_indices[raw_tag])
                #Find the lemma reading:
                lemma_rdg = None
                lemma_ref = '#' + self.lemma
                for rdg in app.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                    if lemma_ref in rdg.get('wit').split():
                        lemma_rdg = rdg
                        break
                #Then proceed through every substantive element in the lemma reading, adding their tags and indices in the Dictionary:
                for lem_rdg_child in lemma_rdg.getchildren():
                    lem_rdg_child_raw_tag = lem_rdg_child.tag.replace('{%s}' % self.tei_ns, '')
                    if lem_rdg_child_raw_tag not in substantive_indices:
                        substantive_indices[lem_rdg_child_raw_tag] = 0
                    else:
                        substantive_indices[lem_rdg_child_raw_tag] += 1
                    segment_type = lem_rdg_child_raw_tag
                    segment_n = str(substantive_indices[lem_rdg_child_raw_tag])
                continue
            #Otherwise, update the current index of the current element's tag in the Dictionary:
            if raw_tag not in substantive_indices:
                substantive_indices[raw_tag] = 0
            else:
                substantive_indices[raw_tag] += 1
            #Then update the current segment name and number:
            segment_type = raw_tag
            segment_n = str(substantive_indices[raw_tag])
        #Now, loop through the <app/> elements added to the lemma XML, adding <lem/> reading elements to them and populating them:
        for app in self.lemma_xml.xpath('//tei:app', namespaces={'tei': self.tei_ns}):
            lem = et.Element('{%s}lem' % self.tei_ns)
            #Find the lemma reading:
            lemma_rdg = None
            lemma_ref = '#' + self.lemma
            for rdg in app.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                if lemma_ref in rdg.get('wit').split():
                    lemma_rdg = rdg
                    break
            #Get the number of substantive elements that appear in the lemma reading:
            n_remaining_children = len(lemma_rdg.getchildren())
            #Then proceed for this many segments after the app element:
            child = app.getnext()
            #If the app element occurs at the end of the document, then there are no children:
            if child is None:
                n_remaining_children = 0
            while n_remaining_children > 0:
                #Skip any non-segment elements (e.g., apparatus elements that have been added):
                if child.tag.replace('{%s}' % self.tei_ns, '') != 'seg':
                    child = child.getnext()
                    continue
                #Move this segment's contents under the <lem/> elements:
                for seg_child in child.getchildren():
                    lem.append(seg_child)
                #Then remove the segment from the lemma and proceed to the next iteration:
                n_remaining_children -= 1            
                child = child.getnext()
            #Ensure that the lemma reading is the first child of the apparatus:
            app.getchildren()[0].addprevious(lem)
        #Finally, desegment the lemma XML:
        segmenter.desegment(self.lemma_xml)
        return
