Changelog
=========


Changes to project.
(Unreleased)

This is a re-write of the application.  The major change is that the previous
code was base on the episode as the unit now is the series.  The paradigm was
to work on a series with multiple episodes and multi-series work was added.
Now the unit is the series since the target always was to work with a
multimedia database with a fair number of series to standardize them.

The usage now is to add series to a queue and start a worker.  If the worker is
running any added series to the queue will be processed.

2.0.0a1 - YYYY-MM-DD
--------------------

- First release
- Re-write of MKVBatchMultiplex
- Use a dark theme on Windows 10
- Add rename for output files
- Jobs table with documented jobs management
- Add Spanish Interface
