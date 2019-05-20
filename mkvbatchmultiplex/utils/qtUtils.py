"""
qtUtils:

utility functions that use PySide2
"""


import logging
import re
import subprocess

from PySide2.QtCore import QMutex, QMutexLocker, Qt
from PySide2.QtWidgets import QDesktopWidget

from ..mediafileclasses import MediaFileInfo
from ..utils import staticVars
from ..jobs import JobStatus

from .mkvUtils import getBaseFiles, getSourceFiles


MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def bVerifyStructure(lstBaseFiles, lstFiles, log=False, currentJob=None):
    """verify the file structure against the base files"""

    for strSource, strFile in zip(lstBaseFiles, lstFiles):

        try:
            objSource = MediaFileInfo(strSource, log)
            objFile = MediaFileInfo(strFile, log)
        except OSError as error:
            if currentJob is not None:
                msg = "pytMediaInfo not found!!!\n"
                msg = msg.format(error.strerror)
                currentJob.outputJobMain(
                    currentJob.jobID,
                    msg,
                    {'color': Qt.red},
                    error=True
                )
            return False

        if objSource != objFile:
            if currentJob is not None:
                msg = "Error: In structure \n{}\n{}\n"
                msg = msg.format(str(objFile), str(objSource))
                currentJob.outputJobMain(
                    currentJob.jobID,
                    msg,
                    {'color': Qt.red},
                    error=True
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

def runCommand(command, currentJob, lstTotal, log=False):
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

            rcResult = p.poll()
            if rcResult is not None:
                rc = rcResult

            if line.find(u"Progress:") == 0:
                # Deal with progress percent
                if addNewline:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "",
                        {'appendLine': True}
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
                    currentJob.outputJobMain(
                        currentJob.jobID, line,
                        {'color': Qt.red, 'appendLine': True},
                        True
                    )
                elif line.find(u"Error") == 0:
                    currentJob.outputJobMain(
                        currentJob.jobID, line,
                        {'color': Qt.red, 'appendLine': True},
                        True
                    )
                    lstTotal[2] += 1
                    if line.find("There is not enough space") >= 0:
                        currentJob.controlQueue.put(JobStatus.AbortJob)
                else:
                    currentJob.outputJobMain(
                        currentJob.jobID, line.strip(), {'appendLine': True}
                    )

            if not currentJob.spControlQueue.empty():
                request = currentJob.spControlQueue.get()
                if request == JobStatus.AbortJob:
                    currentJob.controlQueue.put(JobStatus.AbortJob)
                    p.kill()
                    outs, errs = p.communicate()
                if request == JobStatus.Abort:
                    currentJob.controlQueue.put(JobStatus.AbortForced)
                    p.kill()
                    outs, errs = p.communicate()
                    if outs:
                        print(outs)
                    if errs:
                        print(errs)
                    print(p.returncode)
                    break

        currentJob.outputJobMain(
            currentJob.jobID,
            "\n",
            {'appendLine': True}
        )

    lstTotal[0] += 100

    if log:
        MODULELOG.info("UT007: runCommand rc=%d - %s", rc, command)

    return rc
