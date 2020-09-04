
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

    Python packages are installed if pip is used:

        natsort - natural sorting in Python
        https://natsort.readthedocs.io/en/master/

        pymediainfo - Python MediaInfo wrapper, you can find it at
        https://pypi.org/project/pymediainfo/

        PySide2 - GUI interface library used,
        https://wiki.qt.io/Qt_for_Python

    MKVToolNix - The target tool from witch we get the command,
    https://mkvtoolnix.download/

    MediaInfo library, witch you can find at
    https://mediaarea.net/en/MediaInfo.
    The library has to be available in the PATH environment variable.

For macOS and Windows the version of pymediainfo comes with a MediaInfo Linux
does not.

Binary installations
====================

Binary packages can be found:

    https://github.com/akai10tsuki/mkvbatchmultiplex/releases

    Linux and macOS binaries need more testing.

All binaries are for 64 bit architecture.

Windows:

  - MKVBatchMultiplex-iss-AMD64-X.X.X.exe
    - Regular installation file
  - MKVBatchMultiplex-X.X.X-portable.exe
    - Portable executable
  - MKVBatchMultiplex-portable-dir.zip
    - Portable version in directory format may load faster that the standalone
    version

macOS:
  - MKVBatchMultiplex-X.X.X-cmp.dmg
    - Disk image just mount and drag application to Applications folder

Linux:
  - MKVBatchMultiplex-x86_64-X.X.X.AppImage
    - AppImage of the application is a portable version. Make it an executable
    file in order to run it.
    - install MediaInfo library

Known Issues
============

* On macOS 10.14 Mojave:
    - dark theme in MKVToolNix prior to 30.0.0 doesn't work.
