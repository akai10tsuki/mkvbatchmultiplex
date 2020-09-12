
**********************************************
mkvbatchmultiplex: MKVMERGE batch multiplexing
**********************************************

.. |ss| raw:: html

    <strike>

.. |se| raw:: html

    </strike>

.. image:: https://img.shields.io/pypi/v/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex

.. image:: https://img.shields.io/pypi/pyversions/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex

.. image:: https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg
  :target: CODE_OF_CONDUCT.md

.. image:: https://readthedocs.org/projects/mkvbatchmultiplex/badge/?version=latest
  :target: https://mkvbatchmultiplex.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

This project went into a rewrite for version 2.  Rename module was added to
help maintain output file names Plex_ friendly.

**New algorithm will try to solve some mismatched in file structure.**

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

    - lxml_ 4.5.2 or greater
    - natsort_ 7.0.1 or greater
    - pymediainfo_ 4.2.1 or greater
    - PySide2_ 5.14 or greater

  * MediaInfo_ tested with versions 17.10->20.08
  * MKVToolNix_ tested with versions 17.00->49.0.0

In macOS 10.14 Dark theme MKVToolNix has to be version 30.0.0+ to use it.

Usage
=====

It assumed you have working knowledge of using MKVToolNix.  Select a
file make any operations needed copy command to clipboard. Remember to
select and output directory:

    *Multiplexer->Show command line*

Paste command on mkvbatchmultiplex push <Add Queue> is there are no more jobs
push <Start Worker> button and wait.

Step by step examples are in the github repository wiki_.

When the worker is processing a job before starting to work on a set of files
the structure will be checked. If the structure in the pasted in the pasted
command the the files are processed.  If it doesn't match the program will
check track by track and for tracks that don't match and a best match for the
characteristics needed will be searched. With a successful the track will be
substituted with the match.

Roadmap
=======

This is just the base for the project.  The roadmap is:

    * Work on rename module to fetch metadata
    * Work on the Spanish interface translation
    * |ss| Easier installation for linux |se|

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
.. _lxml: https://lxml.de/
.. _natsort: https://github.com/SethMMorton/natsort
.. _wiki: https://github.com/akai10tsuki/mkvbatchmultiplex/wiki
