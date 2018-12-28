#!/usr/bin/env python3

"""File utilities"""

import os
from pathlib import Path

#class FindFileError(Exception): pass

def _find(element, dirPath, matchFunc=os.path.isfile):

    if isinstance(dirPath, str):
        lstPath = pathToList(dirPath)
    else:
        lstPath = dirPath

    for dirname in lstPath:
        candidate = os.path.join(dirname, element)
        if matchFunc(candidate):
            return candidate
    return None

def findFile(element, dirPath=None):
    """Find file in path specified or system PATH"""
    if dirPath is None:
        dirPath = os.getenv('PATH')
    return _find(element, dirPath)

def findDir(element, dirPath=None):
    """Find directory in path specified or system PATH"""
    if dirPath is None:
        dirPath = os.getenv('PATH')
    return _find(element, dirPath, matchFunc=os.path.isdir)

def pathToList(pathVar):
    """Convert a path variable to a list"""

    pathList = []
    bFound = False

    paths = pathVar.split(os.pathsep)

    for path in paths:
        if os.path.isdir(path):
            pathList.append(path)
            if not bFound:
                bFound = True

    if bFound:
        return pathList
    else:
        return None

def setFullPath(strPath, strFile):
    """Set the filename with the fullpath mkvmerge seems to need this didn't work otherwise"""
    return os.path.join(strPath, strFile)

def getFileList(strPath, strExtFilter=None, bFullPath=False):
    """
    Get files in a directory
    strExtFilter in the form -> .ext
    """
    lstFilesFilter = []
    p = Path(strPath)

    lstObjFileNames = [x for x in p.iterdir() if x.is_file()]

    # Filter by type
    if strExtFilter:
        lstObjFileNames = [x for x in lstObjFileNames if x.match('*' + strExtFilter)]

    if not bFullPath:
        lstFilesFilter = [x.name for x in lstObjFileNames]
    else:
        lstFilesFilter = [str(x) for x in lstObjFileNames]

    return lstFilesFilter
