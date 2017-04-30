=====
Usage
=====

To use Drunken Child In The Fog in a project::

    from drunken_child_in_the_fog.core import DrunkenChildInTheFog

    document = DrunkenChildInTheFog(open("file.pdf")).get_document()
    document.everything().containing_text("Hello")

    for page in document.get_pages():
        first_line = page.lines().horizontal().first()
        second_line = page.lines().horizontal().second()
        caption = page.inside(
            first_line.x1, first_line.y1,
            second_line.x2, second_line.y2).text().first()

        vertical_lines = page.lines().vertical()

For more practical example, see `amms-planop2xls`_ project.

.. _amms-planop2xls: http://github.com/mpasternak/amms-planop2xls
