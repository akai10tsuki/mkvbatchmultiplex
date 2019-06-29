#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup.py for mkvbatchmultiplex"""

import io
import os
import shutil

from pathlib import Path
from setuptools import setup

from mkvbatchmultiplex import config

ROOT = os.path.abspath(os.path.dirname(__file__))


def removeTmpDirs():
    """
    delete build directory setup was including files from other builds
    """
    p = Path('.')
    eggDirs = [x for x in p.glob('*.egg-info') if x.is_dir()]
    eggDirs.append(Path('build'))

    for d in eggDirs:
        if d.is_dir():
            shutil.rmtree(d)


def readme():
    """get README.rst"""

    try:
        with io.open(os.path.join(ROOT, 'README.rst'), encoding='utf-8') as f:
            long_description = '\n' + f.read()
    except FileNotFoundError:
        long_description = config.DESCRIPTION
    return long_description

setup(
    name=config.NAME,  # Required
    version=config.VERSION,  # Required
    #version='0.5.3.a2.dev3',
    description=config.DESCRIPTION,  # Required
    long_description=readme(),  # Optional
    author=config.AUTHOR,  # Optional
    author_email=config.EMAIL,  # Optional
    url=config.URL,
    license='MIT',
    classifiers=[  # Optional
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        # Implementation
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=config.KEYWORDS,
    packages=config.PACKAGES,  # Required
    install_requires=config.REQUIRED,
    python_requires=config.PYTHONVERSIONS,
    include_package_data=True,
    entry_points=config.ENTRYPOINTS,  # Optional
    project_urls=config.PROJECTURLS,
)

removeTmpDirs()
