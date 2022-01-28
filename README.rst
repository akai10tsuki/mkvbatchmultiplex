
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

The hiatus will stop soon I will retake the project on January 2022.

This project went into a rewrite for version 2. Rename module was added to
help maintain output file names Plex_ friendly.

**New algorithm will try to solve some mismatches in file structure.**

For release 2.1.0:

Option o save Jobs when they need to be repeated with the source files in the
same location.  Algorithm revisions to work in more cases.

Development version
===================

2.1.0b1.dev4
************

`Windows 10 development version`_ (64-bit).

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

  * Python_ 3.8.1 or greater

    - lxml_ 4.5.2 or greater
    - natsort_ 7.0.1 or greater
    - pymediainfo_ 4.2.1 or greater
    - PySide2_ 5.14 or greater

  * MediaInfo_ tested with versions 17.10->20.08
  * MKVToolNix_ tested with versions 17.00->51.0.0

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

Algorithms explained
====================

When the worker is processing a job before starting to work on a set of files
the structure will be checked. If the structure is the same as in the pasted
command the files are processed.  If it doesn't match the program will behave
according to the algorithm selected.

New algorithms:

With all Algorithms any file that is not flagged with and invalid structure
the results are the same.  They are different when the files are flagged with
and invalid structure on what they do.

  1. **Algorithm 0** current behavior. If the structure check fails no command
     will be executed files have to be logically equal. The resulting file will
     have the same structure as the destination file on the command line.  The
     resulting file is very likely to be the expected result as specified on the
     command line. If no file is flagged random checks usually are sufficient.
     Any flagged file has to be check to fix any problem and maybe run the
     command with MKVToolNix for that file.

  2. **Algorithm 1** if structure check fails it will try to find the tracks
     that best matches the base file and adjust the command accordingly. Any
     track not used in the command will be ignored. If no suitable track found
     no command will not execute. Resulting file structure if the same as in the
     command line but is not as likely to be the desired file as in Algorithm 0.
     Flagged files should be checked to see if the file is ok.

  3. **Algorithm 2** if Algorithm 1 fails tracks without match will be ignored
     and and the command still will execute.  The resulting file **will not** be
     like the destination file in the original command.  It may even be
     unusable. Any flagged has to be check to see if is usable.

Since in some occasions **Algorithm 1** will produce the correct file it will
be set as the default. The original files should never be erased until all the
new files are watched or at least check with a player that the all the tracks
are muxed as needed.

One case in which **Algorithm 2** applies is when some episodes have commentary
audio tracks.  **Algorithm 1** will fail because on files with missing
commentary tracks there will not be enough audio tracks to produce a file with
a structure logically equal. There are more tracks needed than tracks available.
**Algorithm 2** will ignore this and proceed. Additional files with commentary
tracks will be muxed with it.

Other important difference to the current behavior is that text and audio tracks
are match by language not format. For example:

  In the original source the audio is English with flac format and in the
  current file is English with ac3.  This track will be used for muxing the
  files.

For video tracks the language is always ignored in the testing.

Personally I still used **Algorithm 0** because if I close the program without
checking the flagged files just looking in the directory any missing file will
exactly correspond to a flagged file. For more meticulous users **Algorithm 1**
is the better one.

Roadmap
=======

This is just the base for the project.  The roadmap is:

    * Work on rename module to fetch metadata
    * Work on the Spanish interface translation
    * |ss| Easier installation for linux |se|

For linux installations the AppImage binary format will be used for the
forseeable future.

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
.. _Windows 10 development version: https://github.com/akai10tsuki/mkvbatchmultiplex/releases/download/v2.1.0b1.dev4/MKVBatchMultiplex-2.1.0b1.dev4-iss-AMD64.exe
