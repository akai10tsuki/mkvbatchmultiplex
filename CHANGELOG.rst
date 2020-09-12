Changelog
=========

(Unreleased)

Added
~~~~~

- New algorithm will try to find the tracks that best matches the base file

Changed
~~~~~~~

Fixed
~~~~~

- Don't count bad structure match on unused tracks

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
