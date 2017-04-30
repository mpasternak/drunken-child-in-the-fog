#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pdfminer.six==20170419'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='drunken_child_in_the_fog',
    version='0.1.1',
    description="Funky PDF parser API, using PDFMiner.six",
    long_description=readme + '\n\n' + history,
    author="Michał Pasternak",
    author_email='michal.dtz@gmail.com',
    url='https://github.com/mpasternak/drunken_child_in_the_fog',
    packages=[
        'drunken_child_in_the_fog',
    ],
    package_dir={'drunken_child_in_the_fog':
                 'drunken_child_in_the_fog'},
    entry_points={
        'console_scripts': [
            'drunken_child_in_the_fog=drunken_child_in_the_fog.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='drunken_child_in_the_fog',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
