"""
File utilities
"""

from pathlib import Path


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
