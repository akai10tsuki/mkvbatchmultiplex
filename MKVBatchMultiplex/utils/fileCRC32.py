"""
Calculate the crc of a file and add it to the end of the file name of original
and rename it.
"""

import logging

from pathlib import Path, PurePath

from vsutillib.files import crc32
from vsutillib.pyside6 import LineOutput, SvgColor

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

def computeCRC32(**kwargs: str) -> None:
    """List the source files found"""

    output = kwargs.pop("output", None)
    sourceFile = kwargs.pop("sourceFile", None)
    log = kwargs.pop("log", False)

    if sourceFile:
        fileName = Path(sourceFile)

        if fileName.is_file():
            crc = crc32(fileName.resolve())
            newName = (str(fileName.parent.resolve()) + "/" +
                fileName.stem + r" [" + crc + r"]" + fileName.suffix)
            newFileName = PurePath(newName)
            fileName.rename(newFileName)
            msg = f"       File: {fileName.resolve()}\nRenamed: {newFileName}\n"
            output.command.emit(msg,
                                {LineOutput.AppendEnd: True})
            if log:
                    MODULELOG.debug(
                        "File: %s -> Renamed: %s",
                        str(fileName), newName)
        else:
            output.command.emit(f"Problem adding CRC to file:\n{fileName}\n",
                                {LineOutput.AppendEnd: True})
            if log:
                    MODULELOG.error(
                        "[computeCRC32]: Problem adding CRC to file: %s",
                        str(fileName))
