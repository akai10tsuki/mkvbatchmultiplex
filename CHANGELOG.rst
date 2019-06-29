Changelog
=========


Changes to the project.

1.0.1 - 2019-06-29
------------------

Added
~~~~~
- added configuration files to create snap on ubuntu
- added support for external chapters files
- added ability to rename output files using regex
- added rename can be done with and index if regex is to complex

Changed
~~~~~~~
- highlight errors in rename
- remove current working file if job aborted by an error
- application opens on last tab used
- documentation updates
- Major code cleanup and refactoring making it easier to extend

  * functions, methods and properties rename for clarity
  * moving code on modules reusable in other apps to vsutillib modules
    applications will depend on vsutillib

Fixed
~~~~~
- fix regression single quotes escapes on file path mishandled
- fix font for jobs table didn't change correctly
- fix incorrect signal addJobToTableSignal on jobs module
- fix on macOS the read files have to be sorted in order to correctly
  match the sources
- fix directory files read have to be sorted on macOS

0.9.1b1.dev1 - 2019-5-21
------------~~~~~~~~~~~~

Added
~~~~~
- macOS detect if running in Mojave Dark Mode and if running in binary bundle
- added job information label
- generatecommand.py inside the tests directory of the source tree generates
  command for testing purposes based on the contents of the directory
- more thorough check of command line input
- added **Analysis** button to display information of checks of command line
- check if pymediainfo finds MediaInfo library

Changed
~~~~~~~
- documentation updates
- code cleanup:

  * internal references all relative RTD_ works ok now
  * error output revisions
  * better handling of exit request when jobs are running
  * better handling of single quote in file names
  * code refactoring
  * discard unused functions

- rearrange button group to accommodate Analysis button
- program generatecommand.py in the source tests directory tries to find
  mkvmerge binary
- change from PyQt5 to PySide2 base on Qt 5.12 better for macOS Mojave
- move progress bar to the status bar at the bottom of the window
- bump requirement of pymediainfo to 4.0 no check needed for
  MediaInfo library installation

Fixed
~~~~~
- fix line overwritten on mkvmerge output in Job(s) Output tab
- fix detection of of files with quotes in macOS and ubuntu
- fix match problem for attachments it failed check

0.5.3a2.dev3 - 2018-12-18
-------------------------

Added
~~~~~
- Windows install binary

0.5.3a1 - 2018-12-20

.. _RTD: https://mkvbatchmultiplex.readthedocs.io
