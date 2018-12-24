#!/usr/bin/env python3

"""
MKVFormWidget:

Main form

LOG UT009
"""

import logging
import os
import re
import subprocess

from PyQt5.QtCore import QMutex, QMutexLocker, Qt

import mkvbatchmultiplex.VS as vs
from mkvbatchmultiplex.mediafileclasses import MediaFileInfo


MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


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
                vs.getFileList(
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
                MODULELOG.error("UT003: List of files total don't match")
            for lstTmp in lstTypeTotal:
                error = lstTmp[0] + " - " + lstTmp[1]
                objCommand.strError = objCommand.strError + error + "\n"
                if log:
                    MODULELOG.error("UT004: File(s): %s", error)

    return lstSourceFiles

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

@vs.staticVars(strCommand="", lstBaseFiles=[], lstSourceFiles=[])
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
                    MODULELOG.info("UT005: Hit cached information.")

            # lbf and lsf are mutable pass information back here
            # this approach should make it thread safe so
            # qhtProcess command can work on a queue
            if lbf is not None:
                lbf.extend(getFiles.lstBaseFiles)

            if lsf is not None:
                lsf.extend(getFiles.lstSourceFiles)

        if log:
            MODULELOG.info("UT006: Base files: %s", str(getFiles.lstBaseFiles))
            MODULELOG.info("UT007: Source files: %s", str(getFiles.lstSourceFiles))

def runCommand(command, currentJob, lstTotal, log=False):
    """Execute command in a subprocess thread"""

    regEx = re.compile(r"(\d+)")

    iTotal = 0
    rc = 1000

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as p:
        addNewline = False
        iTotal = lstTotal[0]
        n = 0

        for line in p.stdout:

            if line.find(u"Progress:") == 0:
                # Deal with progress percent
                if not addNewline:
                    addNewline = True

                m = regEx.search(line)

                if m:
                    n = int(m.group(1))

                if n > 0:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        line.strip(),
                        {'color': Qt.black, 'replaceLine': True}
                    )

                    currentJob.progressBar.emit(n, iTotal + n)

            else:

                if addNewline:
                    addNewline = False
                    currentJob.outputJobMain(currentJob.jobID, "\n", {'color': Qt.black})

                if not "\n" in line:
                    line = line + "\n"

                if line.find(u"Warning") == 0:
                    currentJob.outputJobMain(currentJob.jobID, line, {'color': Qt.red})
                    currentJob.outputJobError(currentJob.jobID, line, {'color': Qt.red})
                else:
                    currentJob.outputJobMain(currentJob.jobID, line, {'color': Qt.black})

    if n > 0:
        rc = p.poll()

    lstTotal[0] += 100

    if log:
        MODULELOG.info("UT008: mkvmerge rc=%d - %s", rc, command)

    return rc
