# mkvbatchmultiplex: MKVMERGE batch multiplexing



[![image](https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)


Changes since version 2.0.0

- The applications has been ported to [Python 3.12](https://www.python.org/downloads/release/python-3120/) and [PySide6](https://doc.qt.io/qtforpython-6/).
- Added option to compute the CRC-32 of the output files and add it to the end of the file name.
- [MKVToolnix](https://mkvtoolnix.download/) is now embedded to help with the Linux .version
- [MediaInfo](https://mediaarea.net/en/MediaInfo) is now also embedded. [Pymediainfo](https://pymediainfo.readthedocs.io/en/stable/) was providing the library for Windows in the more recent versions of the package.

## Description

mkvbatchmultiplex program is for processing **mkvmerge** command line
and use it as a template to apply the multiplex instructions to all the
files found in the directory. The command line is expected to be taken
from **mkvtoolnix-gui**:

*Multiplexer-\>Show command line*

**mkvmerge** and **mkvtoolnix-gui** are part of the
[MKVToolNix](https://mkvtoolnix.download/) set of tools to work with
[Matroska](https://www.matroska.org/) media container files.

Works with Windows (cmd.exe) or Linux/unix shells (bash, zsh, etc.)

## Installation

``` bash
pip install mkvbatchmultiplex
```

It is been developed on Windows the media server is Windows based. Made
light testing on ubuntu. Will try to do more testing in linux ubuntu at
least. Many reports of not woriking on linux are solved by installing
[MediaInfo](https://mediaarea.net/en/MediaInfo) this is an external
dependency.

macOS will no longer be supported don\'t have harware to make tests.

If working with the source to execute the application first create the
locale files. On the source directory execute:

``` bash
python setup.py generate_catalog
```

### Dependencies

> -   [Python](https://www.python.org/downloads/) 3.12.1 or greater
>     -   [lxml](https://lxml.de/) 5.1.0 or greater
>     -   [natsort](https://github.com/SethMMorton/natsort) 8.4.0 or
>         greater
>     -   [pymediainfo](https://pypi.org/project/pymediainfo/) 6.1.0 or
>         greater
>     -   [PySide6]() 6.6.1 or greater
> -   [MediaInfo](https://mediaarea.net/en/MediaInfo) tested with
>     versions 17.10-\>23.11.1
> -   [MKVToolNix](https://mkvtoolnix.download/) tested with versions
>     17.00-\>82.0.0

## Usage

It assumed you have working knowledge of using MKVToolNix. Select a file
make any operations needed copy command to clipboard. Remember to select
and output directory:

> *Multiplexer-\>Show command line*

Paste command on mkvbatchmultiplex push \<Add Queue\> is there are no
more jobs push \<Start Worker\> button and wait.

Step by step examples are in the github repository
[wiki](https://github.com/akai10tsuki/mkvbatchmultiplex/wiki).

# Algorithms explained

When the worker is processing a job before starting to work on a set of
files the structure will be checked. If the structure is the same as in
the pasted command the files are processed. If it doesn\'t match the
program will behave according to the algorithm selected.

New algorithms:

With all Algorithms any file that is not flagged with and invalid
structure the results are the same. They are different when the files
are flagged with and invalid structure on what they do.

> 1.  **Algorithm 0** current behavior. If the structure check fails no
>     command will be executed files have to be logically equal. The
>     resulting file will have the same structure as the destination
>     file on the command line. The resulting file is very likely to be
>     the expected result as specified on the command line. If no file
>     is flagged random checks usually are sufficient. Any flagged file
>     has to be check to fix any problem and maybe run the command with
>     MKVToolNix for that file.
> 2.  **Algorithm 1** if structure check fails it will try to find the
>     tracks that best matches the base file and adjust the command
>     accordingly. Any track not used in the command will be ignored. If
>     no suitable track found no command will not execute. Resulting
>     file structure if the same as in the command line but is not as
>     likely to be the desired file as in Algorithm 0. Flagged files
>     should be checked to see if the file is ok.
> 3.  **Algorithm 2** if Algorithm 1 fails tracks without match will be
>     ignored and and the command still will execute. The resulting file
>     **will not** be like the destination file in the original command.
>     It may even be unusable. Any flagged has to be check to see if is
>     usable.

Since in some occasions **Algorithm 1** will produce the correct file it
will be set as the default. The original files should never be erased
until all the new files are watched or at least check with a player that
the all the tracks are muxed as needed.

One case in which **Algorithm 2** applies is when some episodes have
commentary audio tracks. **Algorithm 1** will fail because on files with
missing commentary tracks there will not be enough audio tracks to
produce a file with a structure logically equal. There are more tracks
needed than tracks available. **Algorithm 2** will ignore this and
proceed. Additional files with commentary tracks will be muxed with it.

Other important difference to the current behavior is that text and
audio tracks are match by language not format. For example:

> In the original source the audio is English with flac format and in
> the current file is English with ac3. This track will be used for
> muxing the files.

For video tracks the language is always ignored in the testing.

Personally I still used **Algorithm 0** because if I close the program
without checking the flagged files just looking in the directory any
missing file will exactly correspond to a flagged file. For more
meticulous users **Algorithm 1** is the better one.

## Roadmap

This is just the base for the project. The roadmap is:

> -   Work on rename module to fetch metadata
> -   Work on the Spanish interface translation
> -   Easier installation for linux

For linux installations the AppImage binary format will be used for the
forseeable future.

If the the program generates any interest any further changes and
additions will **also** depend on user base needs.
