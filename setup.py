#!/usr/bin/env python
# -*- coding: utf-8 -*-"""Setup.py for mkvbatchmultiplex"""

import io
import os

from setuptools import setup, find_packages

DESCRIPTION = 'A mkv media batch multiplex.'
KEYWORDS = 'mkv multimedia video'
NAME = "mkvbatchmultiplex"
REQUIRED = [
    'pymediainfo>=2.2.1',
    'PyQt5>=5.10.1'
]
URL='https://github.com/akai10tsuki/mkvbatchmultiplex'
VERSION = None


ROOT = os.path.abspath(os.path.dirname(__file__))


def readme():
    try:
        with io.open(os.path.join(ROOT, 'README.rst'), encoding='utf-8') as f:
            long_description = '\n\n' + f.read()
    except FileNotFoundError:
        long_description = DESCRIPTION
    return long_description

def version():
    """Load the package's __version__.py module as a dictionary."""

    about = {}

    if VERSION is None:
        with io.open(os.path.join(ROOT, NAME, '__version__.py')) as f:
            exec(f.read(), about)
    else:
        about['__version__'] = VERSION

    return about['__version__']

setup(

    name=NAME,  # Required
    version=version(),  # Required
    description=DESCRIPTION,  # Required
    long_description=readme(),  # Optional
    author='Efrain Vergara',  # Optional
    author_email='akai10tsuki@gmail.com',  # Optional
    url=URL,
    license='MIT',

    classifiers=[  # Optional
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers

        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Operating Systems
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords=KEYWORDS,  # Optional

    packages=find_packages(exclude=['docs', 'tests*',]),  # Required

    install_requires=[
        'pymediainfo>=2.2.1',
        'PyQt5>=5.10.1'
    ],

    python_requires='>=3.6, <4',

    include_package_data=True,

    entry_points={  # Optional
        'console_scripts': [
            'mkvbatchmultiplex=mkvbatchmultiplex.mkvbatchmultiplex:mainApp',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/akai10tsuki/mkvbatchmultiplex/issues',
        'Source': 'https://github.com/akai10tsuki/mkvbatchmultiplex/',
    },
)
