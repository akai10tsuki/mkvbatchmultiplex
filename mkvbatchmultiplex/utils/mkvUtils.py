"""
mkvUtils:

related to mkv application functionality

"""

import ctypes
import glob
import logging
import os
import platform
import shlex
import sys

from pathlib import Path

from .fileUtils import findFile, getFileList
from .utils import RunCommand


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def getMediaInfoLib():
    """find MediaInfo library on system"""

    currentOS = platform.system()

    library_names = ()
    library_fullpath = []

    if currentOS == "Darwin":
        library_names = ("libmediainfo.0.dylib", "libmediainfo.dylib")
    elif currentOS == "Linux":
        library_names = ("libmediainfo.so.0", "libzen.so.0")
    elif currentOS == "Windows":
        library_names = ("MediaInfo.dll",)

    if library_names:

        dirs = sys.path

        # python system path
        for library in library_names:
            libFile = findFile(library, dirs)

            if libFile is not None:
                library_fullpath.append(libFile)
            else:
                # search failed
                return []
    else:
        return []

    return library_fullpath

def getMKVMerge():
    """get the name of the mkvmerge executable in the system"""

    currentOS = platform.system()

    if currentOS == "Darwin":

        lstTest = glob.glob("/Applications/MKVToolNix*")
        if lstTest:
            f = lstTest[0] + "/Contents/MacOS/mkvmerge"
            mkvmerge = Path(f)
            if mkvmerge.is_file():
                return mkvmerge

    elif currentOS == "Windows":

        defPrograms64 = os.environ.get('ProgramFiles')
        defPrograms32 = os.environ.get('ProgramFiles(x86)')

        dirs = []
        if defPrograms64 is not None:
            dirs.append(defPrograms64)

        if defPrograms32 is not None:
            dirs.append(defPrograms32)

        # search 64 bits
        for d in dirs:
            search = sorted(Path(d).rglob("mkvmerge.exe"))
            if search:
                mkvmerge = Path(search[0])
                if mkvmerge.is_file():
                    return mkvmerge

    elif currentOS == "Linux":

        search = findFile("mkvmerge")

        if search is not None:
            mkvmerge = Path(search)
            if mkvmerge.is_file():
                return mkvmerge

    return None

def getMKVMergeVersion(mkvmerge):
    """get mkvmerge version"""

    s = mkvmerge

    if s[0:1] != "'" and s[-1:] != "'":
        s = shlex.quote(s)
        print(s)

    runCmd = RunCommand(s + " --version", regexsearch=r" v(.*?) ")

    if runCmd.run():
        return runCmd.regexmatch

    return None

def getBaseFiles(objCommand, log=False):
    """get the base files from the command"""

    lstBaseFiles = []

    if objCommand and objCommand.lstObjFiles:

        # list of base source files the ones received on command line
        lstBaseFiles = \
            [x.fullPathName for x in objCommand.lstObjFiles]

    else:
        if log:
            MODULELOG.error("UT001: Base files reading error")

    return lstBaseFiles

def bCheckLenOfLists(lstLists, lstTypeTotal):
    """list of source files has to be equal length"""

    intTmp = None
    bReturn = True

    for lstTmp in lstLists:

        if not lstTmp:
            bReturn = False
            lstTypeTotal.append(("Ops!!!", "File not found."))
            break

        lstTypeTotal.append([str(len(lstTmp)), os.path.splitext(lstTmp[0])[1]])

        if not intTmp:
            intTmp = len(lstTmp)
        else:
            if len(lstTmp) != intTmp:
                if bReturn:
                    bReturn = False

    return bReturn

def getSourceFiles(objCommand, log=False):
    """read source directories to get files"""

    lstMKVFiles = []
    lstSourceFiles = []
    lstTypeTotal = []

    # Get files from any directory found in command
    # the number of files on each directory has to be equal
    # Filter by type in original source file

    if objCommand and objCommand.lstObjFiles:

        for objFile in objCommand.lstObjFiles:
            lstMKVFiles.append(
                getFileList(
                    objFile.directory,
                    objFile.extension,
                    True
                )
            )

        if bCheckLenOfLists(lstMKVFiles, lstTypeTotal):

            # Join all source files in a list of lists each element
            # have all source files in the order found
            # That is the names are not used the order in the directories is
            for i in range(len(lstMKVFiles[0])):
                lstSourceFiles.append([x[i] for x in lstMKVFiles])
        else:
            objCommand.bRaiseError = True
            error = "UT002: List of files total don't match."
            objCommand.strError = error + "\n\n"
            if log:
                MODULELOG.error("UT002: List of files total don't match")
            for lstTmp in lstTypeTotal:
                error = lstTmp[0] + " - " + lstTmp[1]
                objCommand.strError = objCommand.strError + error + "\n"
                if log:
                    MODULELOG.error("UT003: File(s): %s", error)

    return lstSourceFiles

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
