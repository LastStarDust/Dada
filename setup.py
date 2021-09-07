#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2021 AXELSPACE

import glob

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='dada',
    version='0.0.1',
    author='Pintaudi Giorgio',
    author_email='giorgio.pimpa@gmail.com',
    include_package_data=True,
    zip_safe=True,
    keywords="Digital Discovery 2",
    description='Set of miscellaneous programs for the DIGILENT Digital Discovery 2',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='data/markdown',
    packages=find_packages(),
    scripts=glob.glob('scripts/*.py'),
    license='Proprietary',
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Alpha',
        'Intended Audience :: myself',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: GPL3',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Unix',
    ],
)
