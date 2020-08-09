
**********************************************
mkvbatchmultiplex: MKVMERGE batch multiplexing
**********************************************


.. image:: https://img.shields.io/pypi/v/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex

.. image:: https://img.shields.io/pypi/pyversions/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex


This project went into a rewrite for version 2.  Rename module was added to
help maintain output file names Plex_ friendly.

Description
===========

mkvbatchmultiplex program is for processing **mkvmerge** command line and use
it as a template to apply the multiplex instructions to all the files found
in the directory. The command line is expected to be taken from
**mkvtoolnix-gui**:

*Multiplexer->Show command line*

**mkvmerge** and **mkvtoolnix-gui** are part of the MKVToolNix_ set of tools
to work with Matroska_ media container files.

Works with Windows (cmd.exe) or Linux/unix shells (bash, zsh, etc.)

Installation
============

.. code:: bash

    pip install mkvbatchmultiplex

It is been developed on Windows the media server is Windows based.
Made light testing on ubuntu and macOS 10.14 Mojave and ubuntu 18.04.
On macOS MKVToolNix must be version 30.0.0 or higher if working with
Dark Theme.

If working with the source to execute the application first create the
locale files.  On the source directory execute:

.. code:: bash

    python setup.py generate_catalog

Dependencies
************

    * Python_ 3.8.1
        - PySide2_ 5.14 or greater
        - pymediainfo_ 4.2.1 or greater
    * lxml_ 4.5.2 or greater
    * natsort_ 7.0.1 or greater
    * MediaInfo_ tested with versions 17.10->18.12
    * MKVToolNix_ tested with versions 17.00->46.0.0

For now is a python package it can be installed:

::

    pip install mkvbatchmultiplex
    or download the source


macOS 10.14 Dark theme MKVToolNix has to be version 30.0.0+

Usage
=====

It assumed you have working knowledge of using MKVToolNix.  Select a
file make any operations needed copy command to clipboard:

    *Multiplexer->Show command line*

Paste command on mkvbatchmultiplex push Process button and wait.
Remember to select and output directory.

Roadmap
=======

This is just the base for the project.  The roadmap is:

    * Work on rename module to fetch some metadata from internet
    * Work on the Spanish interface translation
    * Easier installation for linux

If the the program generates any interest any further changes and additions
will **also** depend on user base needs.

See https://mkvbatchmultiplex.readthedocs.io for more information.

.. Hyperlinks.

.. _Plex: https://www.plex.tv/
.. _pymediainfo: https://pypi.org/project/pymediainfo/
.. _PySide2: https://wiki.qt.io/Qt_for_Python
.. _Python: https://www.python.org/downloads/
.. _MKVToolNix: https://mkvtoolnix.download/
.. _Matroska: https://www.matroska.org/
.. _MediaInfo: https://mediaarea.net/en/MediaInfo
.. _AVI: https://docs.microsoft.com/en-us/windows/win32/directshow/avi-file-format/
.. _SRT: https://matroska.org/technical/specs/subtitles/srt.html
.. _lxml: https://lxml.de/
.. _natsort: https://github.com/SethMMorton/natsort
