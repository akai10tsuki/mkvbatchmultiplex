Changelog
=========


Changes to project.
(Unreleased)

This is a re-write of the application.  The major internal change is that the
previous code was base on the episode as the unit of work.  Now the unit is the
series since the target always was to work with a multimedia database with a
fair number of series to standardize them.  Also the tha multimedia was to be
served by Plex_ so a rename module is added to help to keep the names Plex
friendly.

The usage now is to add series to a queue and start a worker.  If the worker is
running any added series to the queue will be processed.

2.0.0a1 - YYYY-MM-DD
--------------------

- First release version 2.0
- Re-write of MKVBatchMultiplex
- Use a dark theme on Windows 10
- Add rename for output files
- Jobs table with jobs management
- Add Spanish Interface

.. Hyperlinks.

.. _Plex: https://www.plex.tv/
