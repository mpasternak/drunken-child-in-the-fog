#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drunken_child_in_the_fog
----------------------------------

Tests for `drunken_child_in_the_fog` module.
"""
import os

import pytest

from drunken_child_in_the_fog.core import DrunkenChildInTheFog


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