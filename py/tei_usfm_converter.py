#!/usr/bin/env python3

import argparse
from lxml import etree as et
import re

"""
XML namespaces
"""
xml_ns = "http://www.w3.org/XML/1998/namespace"
tei_ns = "http://www.tei-c.org/ns/1.0"

"""
USFM abbreviations dictionary
"""
usfm_abbrevations = {
    "Genesis": "GEN",
    "Exodus": "EXO",
    "Leviticus": "LEV",
    "Numbers": "NUM",
    "Deuteronomy": "DEU",
    "Joshua": "JOS",
    "Judges": "JDG",
    "Ruth": "RUT",
    "1 Samuel": "1SA",
    "2 Samuel": "2SA",
    "1 Kings": "1KI",
    "2 Kings": "2KI",
    "1 Chronicles": "1CH",
    "2 Chronicles": "2CH",
    "Ezra": "EZR",
    "Nehemiah": "NEH",
    "Esther": "EST",
    "Job": "JOB",
    "Psalms": "PSA",
    "Proverbs": "PRO",
    "Ecclesiastes": "ECC",
    "Song of Songs": "SNG",
    "Isaiah": "ISA",
    "Jeremiah": "JER",
    "Lamentations": "LAM",
    "Ezekiel": "EZK",
    "Daniel": "DAN",
    "Hosea": "HOS",
    "Joel": "JOL",
    "Amos": "AMO",
    "Obadiah": "OBA",
    "Jonah": "JON",
    "Micah": "MIC",
    "Nahum": "NAM",
    "Habakkuk": "HAB",
    "Zephaniah": "ZEP",
    "Haggai": "HAG",
    "Zechariah": "ZEC",
    "Malachi": "MAL"
}

"""
SBL abbreviations dictionary
"""
sbl_abbrevations = {
    "Genesis": "Gen",
    "Exodus": "Exod",
    "Leviticus": "Lev",
    "Numbers": "Num",
    "Deuteronomy": "Deut",
    "Joshua": "Josh",
    "Judges": "Judg",
    "Ruth": "Ruth",
    "1 Samuel": "1 Sam",
    "2 Samuel": "2 Sam",
    "1 Kings": "1 Kgs",
    "2 Kings": "2 Kgs",
    "1 Chronicles": "1 Chr",
    "2 Chronicles": "2 Chr",
    "Ezra": "Ezra",
    "Nehemiah": "Neh",
    "Esther": "Esth",
    "Job": "Job",
    "Psalms": "Pss",
    "Proverbs": "Prov",
    "Ecclesiastes": "Eccl",
    "Song of Songs": "Song",
    "Isaiah": "Isa",
    "Jeremiah": "Jer",
    "Lamentations": "Lam",
    "Ezekiel": "Ezek",
    "Daniel": "Dan",
    "Hosea": "Hos",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obadiah": "Obad",
    "Jonah": "Jonah",
    "Micah": "Mic",
    "Nahum": "Nah",
    "Habakkuk": "Hab",
    "Zephaniah": "Zeph",
    "Haggai": "Hag",
    "Zechariah": "Zech",
    "Malachi": "Mal"
}

"""
Class for converting a transcription (including collation data) in TEI XML format to USFM format.
"""
class tei_usfm_converter:
    def __init__(self, **kwargs):
        # Populate a String referring to the book's filename base:
        self.filebase = kwargs["filebase"] if "filebase" in kwargs else ""
        # Populate a Dictionary of witness sigla, keyed by witness references (e.g., "#WLC"):
        self.wit_sigla = kwargs["wit_sigla"] if "wit_sigla" in kwargs else {}
        # Populate a Set of ignored apparatus types:
        self.ignored_app_types = kwargs["ignored_app_types"] if "ignored_app_types" in kwargs else set()
        # Initialize counters for the current chapter and verse:
        self.chapter_n = ""
        self.verse_n = ""
        # Initialize a flag indicating whether or not we're currently processing an apparatus entry:
        self.app_flag = False
        return
        
    """
    Recursively converts a transcription (including collation data) in TEI XML format to USFM format.
    """
    def to_usfm(self, xml):
        usfm = ""
        # If the input is an XML tree and not an element, then return the serialization of its root element:
        if not et.iselement(xml):
            usfm += self.to_usfm(xml.getroot())
            # Post-process this USFM text, moving open section paragraph breaks before new chapters to a position after the new chapters
            # and removing superfluous line breaks and spaces:
            usfm = re.sub(r"\\p\s*\\c (\d+)\s*\\m", r"\\c \1\n\\p", usfm)
            usfm = usfm.replace("\n\n", "\n")
            usfm = usfm.replace("  ", " ")
            return usfm
        # Otherwise, proceed according to the tag of the current element:
        raw_tag = xml.tag.replace("{%s}" % tei_ns, "")
        # If this element is a TEI, teiHeader, fileDesc, titleStmt, text, body or lem element, then process its children recursively:
        if raw_tag in ["TEI", "teiHeader", "fileDesc", "titleStmt", "text", "body", "lem"]:
            for child in xml:
                usfm += self.to_usfm(child)
        # If this element is a title, then extract the English book title from it
        # and print the appropriate ID, header, and TOC macros:
        if raw_tag == "title":
            title_text = xml.text
            if "A collation of" in title_text:
                long_book_name = title_text.replace("A collation of ", "").replace(" in SR", "")
                usfm_abbreviation = usfm_abbrevations[long_book_name]
                sbl_abbreviation = sbl_abbrevations[long_book_name]
                usfm += "\\id %s - Solid Rock Hebrew Bible\n" % usfm_abbreviation
                usfm += "\\h %s\n" % long_book_name
                usfm += "\\toc1 The Book of %s\n" % long_book_name
                usfm += "\\toc2 %s\n" % long_book_name
                usfm += "\\toc3 %s\n" % sbl_abbreviation
        # If this element is a milestone, then print a chapter or verse
        if raw_tag == "milestone":
            unit = xml.get("unit")
            # If this is an incipit, then add a \mt macro for the main title:
            if unit == "incipit":
                usfm += "\\mt "
            # If it is a new chapter, then add a new line followed by a \c macro (or a \bd macro, if we're in a variant reading) followed by the chapter number:
            if unit == "chapter":
                if xml.get("n") is not None:
                    self.chapter_n = xml.get("n").split("K")[1]
                    if self.app_flag:
                        usfm += "\\bd %s:\\bd*" % self.chapter_n
                    else:
                        usfm += "\n\\c %s" % self.chapter_n
                        # Add a no-indent paragraph after it:
                        usfm += "\n\\m"
            # If it is a new verse, then add a \v macro (or a \bd macro, if we're in a variant reading) followed by the verse number:
            if unit == "verse":
                if xml.get("n") is not None:
                    self.verse_n = xml.get("n").split("V")[1]
                    if self.app_flag:
                        usfm += "\\bd %s\\bd* " % self.verse_n
                    else:
                        usfm += "\n\\v %s " % self.verse_n
        # If this element is a pb element, then it is a page break (intended to separate "books" of the Psalms):
        if raw_tag == "pb":
            usfm += "\n\\pb\n"
        # If this element is a lb element with type "open", then it is an open section marker:
        if raw_tag == "lb":
            if xml.get("type") is not None and xml.get("type") == "open":
                if self.app_flag:
                    usfm += "{\u05e4} "
                else:
                    usfm += "{\u05e4}\n\\p\n"
        # If this element is a space element with type "closed", then it is a closed section marker:
        if raw_tag == "space":
            if xml.get("type") is not None and xml.get("type") == "closed":
                if self.app_flag:
                    usfm += "{\u05e1} "
                else:
                    usfm += "{\u05e1} "
        # If this element is an app element, then proceed according to its type:
        if raw_tag == "app":
            app_type = xml.get("type") if xml.get("type") is not None else "substantive"
            # Save the current chapter and verse reference, and get the lemma text to be set in the main text later:
            current_chapter_n = self.chapter_n
            current_verse_n = self.verse_n
            lem = xml.find("tei:lem", namespaces={"tei": tei_ns})
            lem_usfm = self.to_usfm(lem)
            # Then process the apparatus entry if necessary:
            if app_type not in self.ignored_app_types:
                # If this variation unit's type is not an ignored type, then add a text-critical footnote 
                # and surround the lemma with the appropriate marks in the main text.
                # Set the flag for processing apparatus entries:
                self.app_flag = True
                # Add a footnote marker and prefix the apparatus entry by the verse reference 
                # and the appropriate variant type marker:
                usfm += "\\f - \\fr %s:%s \\ft " % (current_chapter_n, current_verse_n)
                if app_type == "addition":
                    usfm += "\u2e06 "
                elif app_type == "transposition":
                    usfm += "\u2e0a "
                elif app_type == "omission":
                    usfm += "\u2e0b "
                else:
                    usfm += "\u2e03 "
                # Then recursively parse the contents of the readings, separated by broken bars:
                usfm += "\u00a6 ".join([self.to_usfm(rdg) for rdg in xml.findall("tei:rdg", namespaces={"tei": tei_ns})])
                # Then close the footnote and turn off the flag for processing apparatus entries:
                usfm += "\\f*"
                self.app_flag = False
                # Add the appropriate critical marks around the lemma text:
                if app_type == "addition":
                    usfm += "\u2e06 "
                elif app_type == "transposition":
                    usfm += "\u2e0a %s\u2e09 " % lem_usfm
                elif app_type == "omission":
                    usfm += "\u2e0b %s\u2e0c " % lem_usfm
                else:
                    usfm += "\u2e03 %s\u2e02 " % lem_usfm
            else:
                # If this variation unit's type is an ignored type, then just print the lemma text:
                usfm += lem_usfm
        # If this element is a rdg element, then print its contents recursively and then print its witnesses in a \fw block:
        if raw_tag == "rdg":
            rdg_usfm = ""
            for child in xml:
                rdg_usfm += self.to_usfm(child)
            # If the reading is empty, then replace it with an en-dash:
            if rdg_usfm == "":
                rdg_usfm = "\u2013 "
            usfm += rdg_usfm
            usfm += "\\fw %s \\fw* " % (" ".join([self.wit_sigla[wit] for wit in xml.get("wit").split()]))
        # If this element is a w element, then print its text, followed by a space:
        if raw_tag == "w":
            usfm += xml.text + " "
        # Finally, return the parsed USFM text:
        return usfm