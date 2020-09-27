Changelog
=========

(Unreleased)

Added
~~~~~

Changed
~~~~~~~

- **Algorithm 1** changed when comparing tracks for substitution and
  **only one** track is needed.  If for a particular type (Video, Audio, Text)
  **only one** track exits if the language in the comparison has one as
  undetermined the track will be selected. This occurrence is quite common
  on the target cases trying to solve.  This of course is valid for
  **Algorithm 2**.  The language will be set as in the base source.

Fixed
~~~~~

- Fix BUG #7 "Remove" in context menu on Jobs Table was not working

2.1.0a1.dev1 - 2020-16-9
------------------------

Added
~~~~~

- New algorithms:

  - **Algorithm 0** current behavior the resulting file will have the same
    structure as the destination file on the command line.  Any difference in
    structure of the files the command will not execute.  The resulting file is
    very likely to be the expected result as specified on the command line.
    Random checks  will be sufficient.
  - **Algorithm 1** will try to find the tracks that best matches the base file
    and adjust the command accordingly. Any track not used in the command will
    be ignored. If no suitable track found no command will execute. Resulting
    file structure if the save as in the command line but is not as likely to be
    the desired file as in Algorithm 0.  Flagged files should be checked.
  - **Algorithm 2** if Algorithm 1 fails tracks without match will be ignored
    and and the command still will execute.  The resulting file will not be like
    the destination file in the original command.  It may even be unusable.  Any
    flagged has to be check to see if is usable.

- Synchronized scroll in Rename tab (**Original Names:** with **Rename to:**
  text boxes)

- Add support for one track file multiplexing,  this is usually done for
  subtitles (mks) files. The program will accept commands with only one track
  one source.  The destination file will have correct extension mkv, mka or mks.

Changed
~~~~~~~

Fixed
~~~~~

- Don't count bad structure match for unused tracks

2.0.0 - 2000-8-23
-----------------

Changed
~~~~~~~

- locale updates
- Check Files displays files read from the source directory.  Also the contents
  of the destination directory for debug purposes.

Fixed
~~~~~

- python wheel distribution not working
- system tray icon not showing on macOS

2.0.0b1 - 2020-8-8
------------------

Added
~~~~~

- show progress bar on Windows taskbar icon
- view log on optional tab

Changed
~~~~~~~

- configuration now is a dialog for better compatibility with macOS
- use natural sort when reading directories

Fixed
~~~~~

- Fix BUG #1 force escape quotes for mkvmerge executable in Windows
- Fix BUG #3 title of first episode propagating to all episodes
- dummy progress bar icon function on macOS was not working
- removing configuration elements not always working
- spanish locale fixes

2.0.0a1 - 2019-12-5
-------------------

- First release version 2.0
- Re-write of MKVBatchMultiplex
- Use a dark theme on Windows 10
- Add rename for output files
- Jobs table with jobs management
- Add Spanish Interface

.. Hyperlinks.

.. _Plex: https://www.plex.tv/
