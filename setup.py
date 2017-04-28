#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='drunken-child-in-the-fog',
      version='0.1.0',
      description="PDF analyzer using PDFMiner with a Django-like API for querying PDF file",
      author='Michał Pasternak',
      author_email='michal.dtz@gmail.com',
      url='https://github.com/mpasternak/drunken-child-in-the-fog',
      packages=find_packages(),
      install_requires=['PDFMiner',]
      )
