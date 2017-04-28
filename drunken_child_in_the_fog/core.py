# -*- encoding: utf-8 -*-

import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser

PAGE = "__page__"
HORIZONTAL_LINE = "__horizontal_line__"
VERTICAL_LINE = "__vertical_line__"


class NoSuchElement(Exception):
    pass


class Element:
    def __init__(self, page, x1, y1, x2, y2, text):
        self.page = page
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.text = text

    def __repr__(self):
        return "%s, %s, %s, %s, %s" % (self.x1, self.y1, self.x2, self.y2,
                                       self.text)

    def position_in_document(self):
        position_on_page = self.page.width * self.y1 + self.x1
        return self.page.position_in_document() + position_on_page

    def height(self):
        return self.y2 - self.y1


class PDFCoordinatesElement(Element):
    def __init__(self, page, x1, y1, x2, y2, text):
        self.page = page
        self.x1 = x1
        self.y1 = self.page.height - y2
        self.x2 = x2
        self.y2 = self.page.height - y1
        self.text = text


class ElementQuery:
    def __init__(self, elements=None):
        if elements is None:
            elements = []
        self.elements = elements

    def all(self):
        return self.elements

    def __iter__(self):
        return self.elements.__iter__()

    def count(self):
        return len(self.elements)

    def vertical(self):
        return ElementQuery([elem for elem in self.elements if elem.text ==
                             VERTICAL_LINE])

    def horizontal(self):
        return ElementQuery([elem for elem in self.elements if elem.text == \
                             HORIZONTAL_LINE])

    def lines(self):
        return ElementQuery([elem for elem in self.elements if elem.text in (
            HORIZONTAL_LINE, VERTICAL_LINE)])

    def first(self):
        try:
            return self.elements[0]
        except IndexError:
            raise NoSuchElement

    def second(self):
        try:
            return self.elements[1]
        except IndexError:
            raise NoSuchElement

    def inside(self, x1, y1, x2, y2):
        assert x1 <= x2
        assert y1 <= y2
        ret = []
        for element in self.elements:
            if (x1 <= element.x1 < x2 and y1 <= element.y1 < y2) or \
                    (x1 <= element.x2 < x2 and y1 <= element.y2 < y2):
                ret.append(element)
        return ElementQuery(ret)

    def text(self):
        ret = []
        for element in self.elements:
            if element.text not in (HORIZONTAL_LINE, VERTICAL_LINE):
                ret.append(element)
        return ElementQuery(ret)

    def contains_text(self, text):
        return [elem for elem in self.elements if elem.text.find(text)>=0]


class Page:
    def __init__(self, width, height, previous):
        self.width = width
        self.height = height
        self.previous = previous
        self.elements = []

    def add_element(self, x1, y1, x2, y2, text):
        self.elements.append(PDFCoordinatesElement(self, x1, y1, x2, y2, text))
        self.sorted = False

    def position_in_document(self):
        if self.previous is None:
            return 0

        return self.previous.position_in_document() + self.previous.width * \
                                                      self.previous.height

    def sort_elements(self):
        self.elements.sort(key=lambda elem: elem.y1 * self.width + elem.x1)
        self.sorted = True

    def everything(self):
        return ElementQuery(self.elements)

    def inside(self, *args, **kw):
        return self.everything().inside(*args, **kw)

    def starting_from(self, top, left):
        return self.inside(left, top, self.width, self.height)

    def contains_text(self, text):
        return self.everything().contains_text(text)


class Document:
    def __init__(self):
        self.pages = [None]

    def add_page(self, width, height):
        page = Page(width, height, self.pages[-1])
        self.pages.append(page)
        return page

    def everything(self):
        ret = []
        for page in self.get_pages():
            for elem in page.elements:
                ret.append(elem)
        ret.sort(key=lambda elem: elem.position_in_document())
        return ret

    def get_pages(self):
        return self.pages[1:]

    def sort(self):
        for page in self.get_pages():
            page.sort_elements()


class UnknownLineException(Exception):
    pass


class DrunkenChildInTheFog:
    def __init__(self, fp, char_margin=1):
        self.fp = fp

        # Create a PDF parser object associated with the file object.
        self.parser = PDFParser(self.fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        self.document = PDFDocument(self.parser)

        # Check if the document allows text extraction. If not, abort.
        if not self.document.is_extractable:
            raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        self.rsrcmgr = PDFResourceManager()

        # # Create a PDF device object.
        # self.device = PDFDevice(self.rsrcmgr)
        #
        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        self.laparams = LAParams(char_margin=char_margin)

        # Create a PDF page aggregator object.
        self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)

        # Create a PDF interpreter object.
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)

    def parse_obj(self, lt_objs):

        # loop over the object list
        for obj in lt_objs:

            if isinstance(obj, pdfminer.layout.LTLine):
                p1 = obj.pts[0]
                p2 = obj.pts[1]

                if p1 > p2:
                    _tmp = p1
                    p1 = p2
                    p2 = _tmp
                assert p1 <= p2, ("%s %s" % (p1, p2))

                if p1[0] != p2[0] and p1[1] == p2[1]:
                    ltype = HORIZONTAL_LINE
                elif p1[0] == p2[0] and p1[1] != p2[1]:
                    ltype = VERTICAL_LINE
                else:
                    raise UnknownLineException(obj.pts)
                yield (p1[0], p1[1], p2[0], p2[1], ltype)

            # if it's a textbox, debug(text and location
            elif isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                for elem in obj._objs:
                    assert elem.bbox[0] <= elem.bbox[2]
                    assert elem.bbox[1] <= elem.bbox[3]

                    txt = elem.get_text()
                    txt = txt.encode("utf-8").replace("\n", " ").strip()

                    yield (elem.bbox[0], elem.bbox[1],
                           elem.bbox[2], elem.bbox[3],
                           txt)

            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                for elem in self.parse_obj(obj._objs):
                    yield elem

    def get_document(self):
        # loop over all pages in the document

        document = Document()

        for page in PDFPage.create_pages(self.document):
            # read the page into a layout object
            self.interpreter.process_page(page)
            layout = self.device.get_result()

            page = document.add_page(layout.width, layout.height)

            # extract text from this object
            for elem in self.parse_obj(layout._objs):
                page.add_element(*elem)

        document.sort()
        return document
