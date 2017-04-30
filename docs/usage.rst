=====
Usage
=====

To use Drunken Child In The Fog in a project::

    from drunken_child_in_the_fog.core import DrunkenChildInTheFog

    document = DrunkenChildInTheFog(open("file.pdf")).get_document()
    document.everything().containing_text("Hello")

    for page in document.get_pages():

        table_start = page.inside(200, 200, page.width, page.height).\
            lines().horizontal()

        caption = page.inside(table_start.x1, table_start.y1,
                        page.width, page.height).text().first()

For more practical example, see `amms-planop2xls`_ project.

.. _amms-planop2xls: http://github.com/mpasternak/amms-planop2xls
