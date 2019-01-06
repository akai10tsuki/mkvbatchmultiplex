Changelog
=========


Changes to to project should be listed here.

(unreleased)
------------


Added
~~~~~
- macOS detect if running in Mojave Dark Mode and if running in binary bundle
- added job information label
- generatecommand.py inside the tests directory of the source tree generates
  command for testing purposes based on the contents of the directory
- more thorough check of command line input
- added **Analysis** button to display information of checks of command line

Changed
~~~~~~~
- documentation updates
- code cleanup:
  * internal references all relative RTD works ok now
  * error output revisions
  * better handling of exit request when jobs are running
  * better handling of single quote in file names
  * code refactoring
  * discard unused functions
- program generatecommand.py in the source tests directory tries to find
  mkvmerge binary
- change from PyQt5 to PySide2 base on Qt 5.12 better for macOS Mojave
- move progress bar to the status bar at the bottom of the window

Fixed
~~~~~
- fix line overwritten on mkvmerge output in Job(s) Output tab
- fix detection of of files with quotes in macOS and ubuntu

[0.5.3a2.dev3] - 2018-12-18

Added
~~~~~
- Windows install binary

[0.5.3a1] - 2018-12-20