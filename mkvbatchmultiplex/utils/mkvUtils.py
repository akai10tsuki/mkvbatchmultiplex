"""
mkvUtils:

related to mkv application functionality

"""

import ctypes
import platform


def isMediaInfoLib():
    """find MediaInfo library on system"""

    currentOS = platform.system()
    libNames = ()

    if currentOS == "Windows":
        libraryType = ctypes.WinDLL
        libNames = ["MediaInfo.dll"]
    else:
        libraryType = ctypes.CDLL

    if currentOS == "Darwin":
        libNames = ["libmediainfo.0.dylib", "libmediainfo.dylib"]
    elif currentOS == "Linux":
        libNames = ["libmediainfo.so.0", "libzen.so.0"]

    for library in libNames:
        try:
            libFile = libraryType(library) # pylint: disable=W0612
        except OSError:
            return False

    return True
