#!/usr/bin/env python3

"""File utilities"""

import os
from pathlib import Path, PurePath

#class FindFileError(Exception): pass

def findFile(element, dirPath=None):
    """find file in the path"""

    if dirPath is None:
        dirPath = os.getenv('PATH')

    dirs = dirPath.split(os.pathsep)

    for dirname in dirs:
        candidate = Path(PurePath(dirname).joinpath(element))
        if candidate.is_file():
            return candidate

    return None


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