
**********************************************
mkvbatchmultiplex: MKVMERGE batch multiplexing
**********************************************


.. image:: https://img.shields.io/pypi/v/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex

.. image:: https://img.shields.io/pypi/pyversions/mkvbatchmultiplex.svg
  :target: https://pypi.org/project/mkvbatchmultiplex


This project started out of the need to multiplex a library of many video
series using AVI_ container and SRT_ for subtitles to be maintained in a Media
Server. And as the saying goes search for something to use did not find
anything that met my requirements so program it myself.

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

Dependencies
************

    * Python_ 3.5 or greater on system

        - PySide2_ 5.12 or greater
        - pymediainfo_ 4.0 or greater
    * MediaInfo_ tested with versions 17.10->18.12
    * MKVToolNix_ tested with versions 17.00->34.0.0

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

    * Work on a stable release.
    * Easier installation for different operating systems
    * Documentation
    * Work on job queue management

The application works for me as is. If the the program generates any interest
any further changes and additions will depend on user base needs.

Work on binaries started.

See https://mkvbatchmultiplex.readthedocs.io for more information.

.. Hyperlinks.

.. _pymediainfo: https://pypi.org/project/pymediainfo/
.. _PySide2: https://wiki.qt.io/Qt_for_Python
.. _Python: https://www.python.org/downloads/
.. _MKVToolNix: https://mkvtoolnix.download/
.. _Matroska: https://www.matroska.org/
.. _MediaInfo: https://mediaarea.net/en/MediaInfo
.. _AVI: https://docs.microsoft.com/en-us/windows/desktop/directshow/avi-file-format/
.. _SRT: https://matroska.org/technical/specs/subtitles/srt.html
