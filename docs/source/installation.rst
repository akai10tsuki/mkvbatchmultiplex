
************
Installation
************

I'm working on the backbone to maintain the project on GitHub
once is up work on easy installations for the supported
operating system will be made.  If you are a python users
I don't see any problems you using the application right away.

Python package
==============

Python users can install the program using pip python dependencies
will automatically install if not installed.

.. code:: bash

    pip install mkvbatchmultiplex

Dependencies
============

The program uses:

    Python packages are installed is pip is used:

        pymediainfo - Python MediaInfo wrapper, you can find it at
        https://pypi.org/project/pymediainfo/

        PyQt5 - GUI interface library ussed,
        https://pypi.org/project/PyQt5/

    MKVToolNix - The target tool from witch we get the command,
    https://mkvtoolnix.download/

    MediaInfo library, witch you can find at
    https://mediaarea.net/en/MediaInfo.
    The library has to be available in the PATH environment variable.

Known Issues
============

On macOS MKVToolNix and the application don't work on 10.14 mojave.
This is Qt5 related.  Pre-release versions of MKVToolNix and the
PyQt5 library do work.  So after the PyQt5 is and update will be
made.