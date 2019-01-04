#!/usr/bin/env python3

"""
MKVFormWidget:

Main form

LOG UT009
"""

import logging
import re
import subprocess

from PySide2.QtCore import QMutex, QMutexLocker, Qt
from PySide2.QtWidgets import QDesktopWidget

from mkvbatchmultiplex.mediafileclasses import MediaFileInfo
from mkvbatchmultiplex.utils import staticVars

from .mkvUtils import getBaseFiles, getSourceFiles

MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def bVerifyStructure(lstBaseFiles, lstFiles, log=False, currentJob=None):
    """verify the file structure against the base files"""

    for strSource, strFile in zip(lstBaseFiles, lstFiles):

        objSource = MediaFileInfo(strSource, log)
        objFile = MediaFileInfo(strFile, log)

        if objSource != objFile:
            if currentJob is not None:
                currentJob.outputJobMain(
                    currentJob.jobID,
                    "\n\nError: In structure \n" \
                    + str(objFile) \
                    + "\n"
                    + str(objSource) \
                    + "\n\n",
                    {'color': Qt.red}
                )
                currentJob.outputJobError(
                    currentJob.jobID,
                    "\n\nError: In structure \n"
                    + str(objFile)
                    + "\n"
                    + str(objSource)
                    + "\n\n",
                    {'color': Qt.red}
                )
            return False

    return True

def centerWidgets(widget, parent=None):
    """center widget based on parent or screen geometry"""

    if parent is None:
        parent = widget.parentWidget()

    if parent:
        #hostRect = parent.geometry()
        #widget.move(hostRect.center() - widget.rect().center())

        # cP = parent.rect().center

        #qR = widget.frameGeometry()
        #cP = parent.rect().center()
        #qR.moveCenter(cP)
        #widget.move(qR.topLeft())

        widget.move(parent.rect().center() - widget.frameGeometry().center())

    else:

        widget.move(QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center())

@staticVars(strCommand="", lstBaseFiles=[], lstSourceFiles=[])
def getFiles(objCommand=None, lbf=None, lsf=None, clear=False, log=False):
    """Get the list of files to be worked on in thread safe manner"""

    with QMutexLocker(MUTEX):
        if clear:
            getFiles.strCommand = ""
            getFiles.lstBaseFiles = []
            getFiles.lstSourceFiles = []

        if objCommand is not None:
            if objCommand.strShellcommand != getFiles.strCommand:
                # Information not in cache.
                getFiles.strCommand = objCommand.strShellcommand
                getFiles.lstBaseFiles = getBaseFiles(objCommand, log=log)
                getFiles.lstSourceFiles = getSourceFiles(objCommand, log=log)
            else:
                if log:
                    MODULELOG.info("UT004: Hit cached information.")

            # lbf and lsf are mutable pass information back here
            # this approach should make it thread safe so
            # qhtProcess command can work on a queue
            if lbf is not None:
                lbf.extend(getFiles.lstBaseFiles)

            if lsf is not None:
                lsf.extend(getFiles.lstSourceFiles)

        if log:
            MODULELOG.info("UT005: Base files: %s", str(getFiles.lstBaseFiles))
            MODULELOG.info("UT006: Source files: %s", str(getFiles.lstSourceFiles))

def runCommand(command, currentJob, lstTotal, log=False, ctrlQueue=None):
    """Execute command in a subprocess thread"""

    regEx = re.compile(r"(\d+)")

    iTotal = 0
    rc = 1000

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as p:
        addNewline = True
        iTotal = lstTotal[0]
        n = 0

        for line in p.stdout:

            if line.find(u"Progress:") == 0:
                # Deal with progress percent
                if addNewline:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "",
                        {}
                    )
                    addNewline = False

                m = regEx.search(line)

                if m:
                    n = int(m.group(1))

                if n > 0:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        line.strip(),
                        {'replaceLine': True}
                    )
                    currentJob.progressBar.emit(n, iTotal + n)

            else:

                #if  not line.strip("\n"):
                #    currentJob.outputJobMain(currentJob.jobID, "\n\n", {})
                #else:
                if line.find(u"Warning") == 0:
                    currentJob.outputJobMain(currentJob.jobID, line.strip(), {'color': Qt.red})
                    currentJob.outputJobError(currentJob.jobID, line.strip(), {'color': Qt.red})
                else:
                    currentJob.outputJobMain(currentJob.jobID, line.strip(), {})

            rcResult = p.poll()
            if rcResult is not None:
                rc = rcResult

        if addNewline:
            currentJob.outputJobMain(
                currentJob.jobID,
                "\n",
                {}
            )

    lstTotal[0] += 100

    if log:
        MODULELOG.info("UT007: mkvmerge rc=%d - %s", rc, command)

    return rc
