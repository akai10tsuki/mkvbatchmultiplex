"""
Calculate the crc of a file and add it to the end of the file name of original
and rename it.
"""

import logging
import subprocess

from pathlib import Path, PurePath

from vsutillib.mkv import getMKVMergeEmbedded

from .kwargsKeys import KwargsKey

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

def executeMKVToolnix(appDir, **kwargs: str) -> None:
    """List the source files found"""

    log = kwargs.pop(KwargsKey.log, False)
    output = kwargs.pop(KwargsKey.output, None)

    if appDir:
        mkvtoolnixGUI = getMKVMergeEmbedded(rootDir=appDir, gui=True)

        if mkvtoolnixGUI.is_file():
             subprocess.Popen(mkvtoolnixGUI)

        else:
            if output:
                output.command.emit(f"Can't find embedded mkvtoolnix-gui.")
            if log:
                MODULELOG.error("Can't find embedded mkvtoolnix-gui.")