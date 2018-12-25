
**********************************************
mkvbatchmultiplex: MKVMERGE batch multiplexing
**********************************************

This project started out of the necessity to multiplex a library of many series
using AVI_ container and SRT_ for subtitles to be maintained in a Media Server.
And as the saying goes search for something to use did not find anything that
met my requirements so program it myself.

Description
===========

mkvbatchmultiplex program is for processing **mkvmerge** command line and use
it as a template to apply the multiplex instructions to all the files found
in the directory. The command line is expected to be taken from
**mkvtoolnix-gui**:

*Multiplexer->Show command line*

**mkvmerge** and **mkvtoolnix-gui** are part of the MKVToolNix_ set of tools
to work with Matroska_ media container files.

Works with either Windows (cmd.exe) or Linux/unix shells (bash, zsh, etc.)

Installation
============

If you just can wait for an easier way.  It is been developed on Windows the
media server is Windows based.  Made light testing on ubuntu and macOS.  On
macOS 10.14 mojave it does not work the color palette makes it unusable.  This
a Qt5 problem version 5.12 is working on it when released it will work.
MKVToolNix have the same problem have to wait for version 29.0.0+.
Done some testing with pre-release versions and works more or less find.

Dependencies
************

    * Python_ 3.6 or greater on system
        - PyQt5_ 5.10.1 or greater
        - pymediainfo_ 2.2.1 or greater
    * MediaInfo_ tested with versions 17.10->18.12
    * MKVToolNix_ tested with versions

For now is a python package it can be installed:

::

    pip install mkvbatchmultiplex
    or download the source


macOS 10.14 Dark theme won't work.

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

If the the program generates interest any further changes and additions will
depend on any user base needs.


See https://mkvbatchmultiplex.readthedocs.io for more information.

.. Hyperlinks.

.. _pymediainfo: https://pypi.org/project/pymediainfo/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _Python: https://www.python.org/downloads/
.. _MKVToolNix: https://mkvtoolnix.download/
.. _Matroska: https://www.matroska.org/
.. _MediaInfo: https://mediaarea.net/en/MediaInfo
.. _AVI: https://docs.microsoft.com/en-us/windows/desktop/directshow/avi-file-format/
.. _SRT: https://matroska.org/technical/specs/subtitles/srt.html
