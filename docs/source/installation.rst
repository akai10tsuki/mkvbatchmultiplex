
************
Installation
************

I'm working on the backbone to maintain the project on GitHub
once is up work on easy installations for the supported
operating system will be made.  If you are a python user
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

        PySide2 - GUI interface library used,
        https://wiki.qt.io/Qt_for_Python

    MKVToolNix - The target tool from witch we get the command,
    https://mkvtoolnix.download/

    MediaInfo library, witch you can find at
    https://mediaarea.net/en/MediaInfo.
    The library has to be available in the PATH environment variable.

Known Issues
============

* On macOS 10.14 Mojave:
    - dark theme MKVToolNix prior to 30.0.0
      don't work.
    - binary install always uses light theme
      this is not the case for the python install
