#!/usr/bin/env python

import os
import re
import sys
import sysconfig
import platform
import subprocess
import shutil

from setuptools import setup


# ---------------------------------------------------------------------------- #
def get_project_version():
    # open "VERSION"
    with open(os.path.join(os.getcwd(), 'VERSION'), 'r') as f:
        data = f.read().replace('\n', '')
    # make sure is string
    if isinstance(data, list) or isinstance(data, tuple):
        return data[0]
    else:
        return data


# ---------------------------------------------------------------------------- #
def get_long_description():
    long_descript = ''
    try:
        long_descript = open('README.md').read()
    except:
        long_descript = ''
    return long_descript


# ---------------------------------------------------------------------------- #
def get_short_description():
    return "A collection of scripts for Shifter @ NERSC"


# ---------------------------------------------------------------------------- #
def get_keywords():
    return [ 'ldd', 'otool', 'vtune' ]


# ---------------------------------------------------------------------------- #
def get_classifiers():
    return [
        # development status
        'Development Status :: 5 - Production/Stable',
        # performance monitoring
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # can be used for all of below
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        # written in English
        'Natural Language :: English',
        # MIT license
        'License :: OSI Approved :: MIT License',
        # tested on these OSes
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
        # written in C++, available to Python via PyBind11
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]


# ---------------------------------------------------------------------------- #
def get_name():
    return 'Jonathan R. Madsen'


# ---------------------------------------------------------------------------- #
def get_email():
    return 'jrmadsen@lbl.gov'


# ---------------------------------------------------------------------------- #
# calls the setup and declare package
setup(name='shiftercp',
      version=get_project_version(),
      author=get_name(),
      author_email=get_email(),
      maintainer=get_name(),
      maintainer_email=get_email(),
      contact=get_name(),
      contact_email=get_email(),
      description=get_short_description(),
      long_description=get_long_description(),
      long_description_content_type='text/markdown',
      url='https://github.com/jrmadsen/shifter-tools.git',
      license='MIT',
      zip_safe=True,
      py_modules = ['shiftercp'],
      keywords=get_keywords(),
      classifiers=get_classifiers(),
      python_requires='>=2.6',
      )
