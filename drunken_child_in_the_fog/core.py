# -*- encoding: utf-8 -*-

import sys

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
    """Raised when there's no such :class:`Element`. """
    pass


class Element:
    """Element of a PDF file, with some text inside. Has a bounding box, 
    (x1, y1), (x2, y2). The coordinates system is normalized from PDF 
    notation so Elements have (0,0) in the upper left corner.
    """

    def __init__(self, page, x1, y1, x2, y2, text):
        """
        
        :param page: parent :class:`core.Page` 
        :param x1: lower left 
        :param y1: lower bottom 
        :param x2: upper right
        :param y2: upper top
        :param text: 
        """
        self.page = page
        self.x1 = x1
        self.y1 = self.page.height - y2
        self.x2 = x2
        self.y2 = self.page.height - y1
        self.text = text

    def __repr__(self):
        return "%s, %s, %s, %s, %s" % (self.x1, self.y1, self.x2, self.y2,
                                       self.text)

    def position_in_document(self):
        """Returns a single integer, which gives a position of this element 
        on the page. """
        position_on_page = self.page.width * self.y1 + self.x1
        return self.page.position_in_document() + position_on_page

    def height(self):
        return self.y2 - self.y1


class ElementSet:
    """Class used to query for :class:`.Element`, somehow modelled on 
    `Django QuerySet`_. 
    
    .. _Django QuerySet: https://docs.djangoproject.com/en/1.11/ref/models/quer
    ysets/
    """

    def __init__(self, elements=None):
        if elements is None:
            elements = []
        self.elements = elements

    def all(self):
        """Return a list with every :class:`.Element` in the set. """
        return self.elements

    def __iter__(self):
        return self.elements.__iter__()

    def count(self):
        """Return number of :class:`.Element` in the set. """
        return len(self.elements)

    def __len__(self):
        return self.count()

    def vertical(self):
        """Returns :class:`.ElementSet` containing only vertical lines from current 
        set. """
        return ElementSet([elem for elem in self.elements if elem.text ==
                           VERTICAL_LINE])

    def horizontal(self):
        """Returns :class:`.ElementSet` containing only horizontal lines from 
        current set."""
        return ElementSet([elem for elem in self.elements if elem.text ==
                           HORIZONTAL_LINE])

    def lines(self):
        """Returns :class:`.ElementSet` containing lines from the current set.
         """
        return ElementSet([elem for elem in self.elements if elem.text in (
            HORIZONTAL_LINE, VERTICAL_LINE)])

    def first(self):
        """Returns first Element in set or raises NoSuchElement exception. """
        try:
            return self.elements[0]
        except IndexError:
            raise NoSuchElement

    def second(self):
        """Returns second Element in set or raises NoSuchElement exception. """
        try:
            return self.elements[1]
        except IndexError:
            raise NoSuchElement

    def inside(self, x1, y1, x2, y2):
        """Returns :class:`.ElementSet` which contains every element from the current 
        set contained in a box described by coordinates (x1, y1), (x2, 
        y2). Left-top edge is inclusive, bottom-right is not. """
        assert x1 <= x2
        assert y1 <= y2
        ret = []
        for element in self.elements:
            first_inside = x1 <= element.x1 < x2 and y1 <= element.y1 < y2
            second_inside = x1 <= element.x2 < x2 and y1 <= element.y2 < y2
            if first_inside or second_inside:
                ret.append(element)
        return ElementSet(ret)

    def text(self):
        """Returns :class:`.ElementSet` containing every text element from the current 
        set. """

        ret = []
        for element in self.elements:
            if element.text not in (HORIZONTAL_LINE, VERTICAL_LINE):
                ret.append(element)
        return ElementSet(ret)

    def containing_text(self, text):
        """Returns :class:`.ElementSet` with all elements which have 'text' 
        inside."""
        return ElementSet([elem for elem in self.elements if elem.text.find(
            text) >= 0])


class Page:
    """Page keeps track of all the elements.
    """

    def __init__(self, width, height, previous):
        self.width = width
        self.height = height
        self.previous = previous
        self.elements = []

    def add_element(self, x1, y1, x2, y2, text):
        self.elements.append(Element(self, x1, y1, x2, y2, text))
        self.sorted = False

    def position_in_document(self):
        """This returns a single integer, giving this page position in the
        whole document. It is calculated including every previous page 
        width and height. """
        if self.previous is None:
            return 0

        current_position = self.previous.width + self.previous.hegith
        return self.previous.position_in_document() + current_position

    def sort_elements(self):
        """Sort elements in-place, basing on their position on the page.  """
        self.elements.sort(key=lambda elem: elem.y1 * self.width + elem.x1)
        self.sorted = True

    def everything(self):
        """Return an :class:`.ElementSet` with every single element from this 
        page. """
        return ElementSet(self.elements)

    def inside(self, *args, **kw):
        """Return an :class:`.ElementSet` with every single element from this page, 
        contained in the box specified by args. See Element.inside for 
        details. """
        return self.everything().inside(*args, **kw)

    def starting_from(self, top, left):
        """Return an :class:`.ElementSet` with every single element from this page, 
        contained below coordinates (left, top) specified in parameters. 
        """
        return self.inside(left, top, self.width, self.height)

    def containing_text(self, text):
        """Return an :class:`.ElementSet` with every single element containing text 
        specified by parameter. See Element.contains_text for details. """
        return self.everything().containing_text(text)


class Document:
    """Document holds all pages. """

    def __init__(self):
        self.pages = [None]

    def add_page(self, width, height):
        """Add the next page. """
        page = Page(width, height, self.pages[-1])
        self.pages.append(page)
        return page

    def everything(self):
        """Returns a sorted :class:`.ElementSet` containing every single element, 
        from every single page. Elements are sorted by their position in the 
        document. """
        ret = []
        for page in self.get_pages():
            for elem in page.elements:
                ret.append(elem)
        ret.sort(key=lambda elem: elem.position_in_document())
        return ElementSet(ret)

    def get_pages(self):
        """Return all pages. """
        return self.pages[1:]

    def sort(self):
        """Sort elements in every single page. """
        for page in self.get_pages():
            page.sort_elements()


class UnknownLineException(Exception):
    pass


class DrunkenChildInTheFog:
    """This is who we are, when we enter the real of PDF analysis madness. 
    A drunken children in the fog, looking for their way out.
    
    >>> document = DrunkenChildInTheFog(open("file.pdf")).get_document()
    >>> document.everything()
    """

    def __init__(self, fp, char_margin=1):
        self.fp = fp

        self.parser = PDFParser(self.fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        self.document = PDFDocument(self.parser)

        # Check if the document allows text extraction. If not, abort.

        if not self.document.is_extractable:
            raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        self.rsrcmgr = PDFResourceManager()

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        self.laparams = LAParams(char_margin=char_margin)

        # Create a PDF page aggregator object.
        self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)

        # Create a PDF interpreter object.
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)

    def _parse_obj(self, lt_objs):

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
                    if sys.version_info < (3, 3):
                        txt = txt.encode("utf-8").replace("\n", " ").strip()
                    else:
                        txt = txt.replace("\n", " ").strip()

                    yield (elem.bbox[0], elem.bbox[1],
                           elem.bbox[2], elem.bbox[3],
                           txt)

            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                for elem in self._parse_obj(obj._objs):
                    yield elem

    def get_document(self):
        # loop over all pages in the document

        ret = Document()
        pages = PDFPage.create_pages(self.document)
        for page in pages:
            # read the page into a layout object
            self.interpreter.process_page(page)
            layout = self.device.get_result()

            page = ret.add_page(layout.width, layout.height)

            # extract text from this object
            for elem in self._parse_obj(layout._objs):
                page.add_element(*elem)

        ret.sort()
        return ret
