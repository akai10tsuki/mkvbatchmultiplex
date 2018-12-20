
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


.. Hyperlinks.

.. _MKVToolNix: https://mkvtoolnix.download/
.. _Matroska: https://www.matroska.org/
.. _AVI: https://docs.microsoft.com/en-us/windows/desktop/directshow/avi-file-format/
.. _SRT: https://matroska.org/technical/specs/subtitles/srt.html
