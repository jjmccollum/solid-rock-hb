#!/usr/bin/env python3

from lxml import etree as et
from copy import deepcopy

"""
Class for resegmenting a collation in TEI XML format.
"""
class tei_collation_editor:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    def __init__(self, **kwargs):
        return
    """
    Validates a resegmentation of a given XML tree based on the placement of <divGen/> elements of type "seg".
    """
    def validate(self, xml):
        valid = True
        #Ensure that in every apparatus, all readings have the same number of segment division markers:
        for app in xml.xpath('//tei:app', namespaces={'tei': self.tei_ns}):
            #Get the index of this apparatus, for reference:
            app_n = app.get('n') if app.get('n') is not None else ''
            n_segs = 0
            #Set the number of segment division markers based on the lemma reading:
            lem = app.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
            n_segs = len(lem.xpath('.//tei:divGen[@type=\'seg\']', namespaces={'tei': self.tei_ns}))
            #Now ensure that all variant readings have the same number of segment division markers:
            for rdg in app.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                if len(rdg.xpath('.//tei:divGen[@type=\'seg\']', namespaces={'tei': self.tei_ns})) != n_segs:
                    valid = False
                    print('The apparatus with index ' + app_n + ' has a reading with a different number of segment division markers than the lemma.')
        return valid
    """
    Returns a List of IDs corresponding to witnesses in the collation's <listWit/> element.
    """
    def get_witnesses(self, xml):
        witnesses = []
        #Get the <listWit/> element:
        listWit = xml.xpath('//tei:listWit', namespaces={'tei': self.tei_ns})[0]
        #Then copy the IDs of the witnesses contained in it:
        for witness in listWit.xpath('//tei:witness', namespaces={'tei': self.tei_ns}):
            wit_id = witness.get('id')
            witnesses.append(wit_id)
        return witnesses
    """
    Returns a TEI XML tree containing only the lemma text of the given TEI XML tree.
    """
    def get_lemma_xml(self, xml):
        #Start with a <TEI/> element at the root:
        lemma_xml = et.Element('{%s}TEI' % self.tei_ns, nsmap={None: self.tei_ns, 'xml': self.xml_ns})
        #Add a <text/> element under this with the attributes of the original XML tree's corresponding element:
        lemma_text = et.Element('{%s}text' % self.tei_ns)
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        for attr in text.attrib:
            lemma_text.set(attr, text.get(attr))
        lemma_xml.append(lemma_text)
        #Add a <body/> element under this:
        lemma_body = et.Element('{%s}body' % self.tei_ns)
        lemma_text.append(lemma_body)
        #Then proceed through every element under the original XML tree's <body/> element:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        for child in body:
            #If the element is an apparatus, then add only the elements under its <lem/> child:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'app':
                lem = child.xpath('.//tei:lem', namespaces={'tei': self.tei_ns})[0]
                for lem_child in lem:
                    lemma_body.append(deepcopy(lem_child))
            #Add any other element as-is:
            else:
                lemma_body.append(deepcopy(child))
        return et.ElementTree(lemma_xml)
    """
    Returns a TEI XML tree containing only the text for the given witness from the given TEI XML tree.
    """
    def get_witness_xml(self, xml, wit):
        #Start with a <TEI/> element at the root:
        witness_xml = et.Element('{%s}TEI' % self.tei_ns, nsmap={None: self.tei_ns, 'xml': self.xml_ns})
        #Add a <text/> element under this with the attributes of the original XML tree's corresponding element:
        witness_text = et.Element('{%s}text' % self.tei_ns)
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        for attr in text.attrib:
            witness_text.set(attr, text.get(attr))
        witness_xml.append(witness_text)
        #Add a <body/> element under this:
        witness_body = et.Element('{%s}body' % self.tei_ns)
        witness_text.append(witness_body)
        #Then proceed through every element under the original XML tree's <body/> element:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        for child in body:
            #If the element is an apparatus, then add only the elements under the appropriate <rdg/> child:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'app':
                wit_rdg = et.Element('{%s}rdg' % self.tei_ns)
                for rdg in child.xpath('.//tei:rdg', namespaces={'tei': self.tei_ns}):
                    wit_ref = '#' + wit
                    if wit_ref in rdg.get('wit').split():
                        wit_rdg = rdg
                        break
                for wit_rdg_child in wit_rdg:
                    witness_body.append(deepcopy(wit_rdg_child))
            #Add any other element as-is:
            else:
                witness_body.append(deepcopy(child))
        return et.ElementTree(witness_xml)
    """
    Segments a TEI XML tree based on the placement of <divGen/> elements of type "seg".
    """
    def segment(self, xml):
        #Get the <text/> element in the XML tree:
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        #Get the <body/> element under it:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        #Create a new element to replace it, which we'll populate with segmented content:
        segmented_body = et.Element('{%s}body' % self.tei_ns)
        #Create a placeholder for the current segment:
        seg = et.Element('{%s}seg' % self.tei_ns)
        for child in body:
            #If this is a <divgen/> element of type "seg", then add the previous segment to the new body and initialize a new segment:
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'divGen' and child.get('type') is not None and child.get('type') == 'seg':
                segmented_body.append(seg)
                seg = et.Element('{%s}seg' % self.tei_ns)
            #Otherwise, add this element to the current segment:
            else:
                seg.append(child)
        #Add the final segment to the body:
        segmented_body.append(seg)
        #Finally, remove the old body from the XML and replace it with the segmented body:
        text.remove(body)
        text.append(segmented_body)
        return
    """
    Updates the boundaries of <app/> elements in a given TEI XML tree based on the placement of <divGen/> elements of type "seg".
    """
    def update_boundaries(self, xml):
        #Get a List of witnesses in this collation:
        witnesses = self.get_witnesses(xml)
        #Extract a segmented version of the lemma's XML:
        lemma_xml = self.get_lemma_xml(xml)
        self.segment(lemma_xml)
        #Extract a segmented version of each witness's XML:
        xml_by_witness = {}
        for wit in witnesses:
            witness_xml = self.get_witness_xml(xml, wit)
            self.segment(witness_xml)
            xml_by_witness[wit] = witness_xml
        #Get the <text/> element in the XML tree:
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        #Get the <body/> element under it:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        #Create a new element to replace it, which we'll populate with updated content:
        updated_body = et.Element('{%s}body' % self.tei_ns)
        #All segmented XML files should have the same number of segments, so compare all witnesses at each segment:
        lem_segs = lemma_xml.xpath('//tei:seg', namespaces={'tei': self.tei_ns})
        for i in range(len(lem_segs)):
            lem_seg = lem_segs[i]
            rdg_segs = [] #segments containing variant readings
            reading_support = {} #map from serializations of variant readings to Lists of IDs for their supporting witnesses
            for wit in witnesses:
                witness_xml = xml_by_witness[wit]
                witness_seg = witness_xml.xpath('//tei:seg', namespaces={'tei': self.tei_ns})[i]
                s = et.tostring(witness_seg, encoding='unicode')
                if s not in reading_support:
                    rdg_segs.append(witness_seg)
                    reading_support[s] = []
                reading_support[s].append(wit)
            #If only one variant is present, then no apparatus is necessary; just add the content of the lemma's segment:
            if len(reading_support) == 1:
                for child in lem_seg:
                    updated_body.append(child)
            #Otherwise, create an apparatus, and add the variant readings:
            else:
                app = et.Element('{%s}app' % self.tei_ns)
                #First, add the lemma reading:
                lem = et.Element('{%s}lem' % self.tei_ns)
                for child in lem_seg:
                    lem.append(child)
                app.append(lem)
                #Then add the variant readings:
                for rdg_seg in rdg_segs:
                    rdg = et.Element('{%s}rdg' % self.tei_ns)
                    s = et.tostring(rdg_seg, encoding='unicode')
                    supporting_wit_refs = ['#' + wit for wit in reading_support[s]]
                    rdg.set('wit', ' '.join(supporting_wit_refs))
                    for child in rdg_seg:
                        rdg.append(child)
                    app.append(rdg)
                #Then add the entire apparatus to the updated body:
                updated_body.append(app)
        #Finally, remove the old body from the XML and replace it with the updated body:
        text.remove(body)
        text.append(updated_body)
        return
