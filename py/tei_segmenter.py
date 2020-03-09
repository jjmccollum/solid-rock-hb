#!/usr/bin/env python3

from lxml import etree as et

"""
Class for segmenting TEI XML transcriptions of Hebrew text.
"""
class tei_segmenter:
    """
    XML namespaces
    """
    xml_ns = 'http://www.w3.org/XML/1998/namespace'
    tei_ns = 'http://www.tei-c.org/ns/1.0'
    """
    Set of tags that should be segmented with the next tag rather than the preceding tag.
    """
    prefix_tags = set([
        'divGen'
    ])
    def __init__(self, **params):
        self.ignored_tag_set = params['t']
    """
    Segments the given normalized TEI XML tree, grouping all ignored elements with substantive elements.
    The segments will be labeled with the tag and numerical index of the substantive element.
    """
    def segment(self, xml):
        #Get the <text/> element in the XML tree:
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        #Get the <body/> element under it:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        #Create a new element to replace it, which we'll populate with segmented content:
        segmented_body = et.Element('{%s}body' % self.tei_ns)
        #Maintain a Dictionary of current substantive element indices:
        substantive_indices = {}
        #Maintain a queue of ignored elements to add to the current segment:
        segment_elements = []
        segment_type = '' #the tag of the substantive element in the current segment:
        segment_n = '' #the index of the substantive element in the current segment:
        pos = 1 #current positioning state (-1 = previous, 0 = current, 1 = next)
        for child in body.getchildren():
            raw_tag = child.tag.replace('{%s}' % self.tei_ns, '')
            #By default, tags will have positioning values of -1:
            child_pos = -1
            #If this is a substantive tag, then its positioning value is 0:
            if raw_tag not in self.ignored_tag_set:
                child_pos = 0
                #Increment the latest index for this element's tag:
                if raw_tag not in substantive_indices:
                    substantive_indices[raw_tag] = 0
                else:
                    substantive_indices[raw_tag] += 1
                #If the segment type has not already been set, then set it to this element's tag,
                #and update the segment number:
                if segment_type == '':
                    segment_type = raw_tag
                    segment_n = str(substantive_indices[raw_tag])
            #Otherwise, if it is a prefix tag, then its positioning value is 1:
            elif raw_tag in self.prefix_tags:
                child_pos = 1
            #If its positioning value is greater than the last element's positioning value, or if both are zero, 
            #then add a new segment and move all of the current elements in the queue to it:
            if child_pos > pos or (child_pos == 0 and pos == 0):
                seg = et.Element('{%s}seg' % self.tei_ns)
                seg.set('type', segment_type)
                seg.set('n', segment_n)
                for segment_element in segment_elements:
                    seg.append(segment_element)
                segmented_body.append(seg)
                segment_elements = []
                #Then reset the segment tag and index to empty values, 
                #or to the values of the current element if it is substantive:
                if raw_tag not in self.ignored_tag_set:
                    segment_type = raw_tag
                    segment_n = str(substantive_indices[raw_tag])
                else:
                    segment_type = ''
                    segment_n = ''
            #Add the current element to the segment:
            segment_elements.append(child)
            #Update the positioning state to that of the current element:
            pos = child_pos
        #Finally, remove the old body from the XML and replace it with the segmented body:
        text.remove(body)
        text.append(segmented_body)
        return
    """
    Desegments a segmented TEI XML tree.
    """
    def desegment(self, xml):
        #Get the <text/> element in the XML tree:
        text = xml.xpath('//tei:text', namespaces={'tei': self.tei_ns})[0]
        #Get the <body/> element under it:
        body = text.xpath('.//tei:body', namespaces={'tei': self.tei_ns})[0]
        #Create a new element to replace it, which we'll populate with desegmented content:
        desegmented_body = et.Element('{%s}body' % self.tei_ns)
        #For each segment element that is a child of the original body, copy its children as children of the desegmented body:
        for child in body.getchildren():
            if child.tag.replace('{%s}' % self.tei_ns, '') == 'seg':
                for segment_element in child.getchildren():
                    desegmented_body.append(segment_element)
            else:
                desegmented_body.append(child)
        #Finally, remove the old body from the XML and replace it with the desegmented body:
        text.remove(body)
        text.append(desegmented_body)
        return
