#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drunken_child_in_the_fog
----------------------------------

Tests for `drunken_child_in_the_fog` module.
"""
import os

import pytest

from drunken_child_in_the_fog.core import DrunkenChildInTheFog, NoSuchElement


@pytest.fixture
def test_file():
    return open(os.path.join(os.path.dirname(__file__), "test.pdf"), "rb")


def test_content(test_file):
    document = DrunkenChildInTheFog(test_file).get_document()

    e = document.everything()
    assert e.count() > 0

    assert e.lines().count() == 0
    assert e.lines().horizontal().count() == 0
    assert e.lines().vertical().count() == 0
    assert e.text().count() > 0
    assert e.containing_text("Hello").count() == 1
    assert e.containing_text("Hello").first().text.startswith("Hello")
    with pytest.raises(NoSuchElement):
        assert e.containing_text("Hello").second()

    page = document.get_pages()[0]
    assert e.inside(0, 0, page.width, page.height).count() > 0
    assert page.inside(0, 0, page.width, page.height).count() > 0
    assert page.containing_text("Hello").count() == 1

    e = e.all()[0]
    assert e.position_in_document() > 0

    assert str(e) != ""

