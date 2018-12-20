#!/usr/bin/env python3

"""
MKVFormWidget:

Main form

LOG FW025
"""

import logging
import os
import platform
import re
import subprocess

from PyQt5.QtCore import QMutex, QMutexLocker, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
                             QLineEdit, QMessageBox, QPushButton,
                             QWidget)

import mkvbatchmultiplex.library.VS as vs
import mkvbatchmultiplex.library.qththreads as threads

from mkvbatchmultiplex.library.mediafileclasses import MediaFileInfo, MKVCommand
from .MKVOutputWidget import MKVOutputWidget
from .MKVJobsTableWidget import JobStatus


MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CurrentJob(): # pylint: disable=R0903
    """Helper class for working with a job"""

    def __init__(self):

        self.jobID = None
        self.status = None
        self.command = None
        self.outputMain = None
        self.outputJobMain = None
        self.outputJobError = None
        self.progressBar = None


class WorkFiles():
    """Files read from directories"""

    def __init__(self):

        self.baseFiles = []
        self.sourceFiles = []

    def clear(self):
        """Clear file lists"""

        self.baseFiles = []
        self.sourceFiles = []


class WorkerSignals(threads.WorkerSignals):
    """Additional signals for QRunables"""

    progress = pyqtSignal(int, int)
    outputmain = pyqtSignal(str, dict)
    outputcommand = pyqtSignal(str)


class Worker(threads.Worker): # pylint: disable=R0903
    """QRunnable worker with additional callbacks"""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__(fn, *args, **kwargs)

        # Override signals variable with extended one
        self.signals = WorkerSignals()

        # Add the callback to kwargs
        self.kwargs['cbProgress'] = self.signals.progress
        self.kwargs['cbOutputMain'] = self.signals.outputmain
        self.kwargs['cbOutputCommand'] = self.signals.outputcommand


class MKVFormWidget(QWidget):
    """Central widget"""
    # pylint: disable=too-many-instance-attributes
    # Defining elements of a GUI

    RUNNING = False

    def __init__(self, parent, qthThread, jobs, ctrlQueue):
        super(MKVFormWidget, self).__init__(parent)

        self.parent = parent
        self.log = parent.log
        self.threadpool = qthThread
        self.jobs = jobs
        self.controlQueue = ctrlQueue
        self.objCommand = MKVCommand()
        self.lstSourceFiles = []
        self.lstBaseFiles = []

        self._initControls()
        self._initLayout()

    def _initHelper(self):
        self.objCommand = MKVCommand()
        self.lstSourceFiles = []
        self.lstBaseFiles = []

    def _initControls(self):
        """Controls for Widget"""

        self.lblCommand = QLabel("MKVMERGE Command Line")

        # Command line input mkvtoolnix-gui: Multiplexer->Show command line
        self.leCommand = QLineEdit()
        self.leCommand.setClearButtonEnabled(True)
        validator = self.ValidateCommand(self)
        self.leCommand.setValidator(validator)

        self.btnPasteClipboard = QPushButton(" Paste Clipboard ")
        self.btnPasteClipboard.resize(self.btnPasteClipboard.sizeHint())
        if platform.system() != "Linux":
            #macOS will not update if a thread is not used
            #linux - ubuntu won't work with this the first click fails
            #    from there on it work
            #windows - work

            self.btnPasteClipboard.clicked.connect(
                lambda: self.qthRunInThread(self.qthPasteClipboard)
            )
        else:
            #linux - ubuntu only refresh correctly this way
            #macOS - refresh doesn't work must use keyboard arrows to refresh
            #windows - work

            self.btnPasteClipboard.clicked.connect(
                self.pasteClipboard
            )
        self.btnPasteClipboard.setToolTip(
            "Paste copy of <b>mkvtoolnix-gui</b> Show command line"
        )

        self.btnAddQueue = QPushButton(" Add to Job ")
        self.btnAddQueue.resize(self.btnAddQueue.sizeHint())
        self.btnAddQueue.clicked.connect(
            lambda: self.qthRunInThread(self.addQueue)
        )
        self.btnAddQueue.setToolTip(
            "Add command to queue."
        )

        self.btnProcessQueue = QPushButton(" Process Jobs ")
        self.btnProcessQueue.resize(self.btnProcessQueue.sizeHint())
        self.btnProcessQueue.clicked.connect(
            lambda: self.qthRunInThread(self.qthProcessCommand)
        )
        self.btnProcessQueue.setToolTip("Execute batch commands on queue.")

        self.btnPreProcess = QPushButton(" Pre-Process ")
        self.btnPreProcess.resize(self.btnPreProcess.sizeHint())
        self.btnPreProcess.clicked.connect(
            lambda: self.qthRunInThread(self.qthPreProcess)
        )
        self.btnPreProcess.setToolTip(
            "Process the command line to check for errors."
        )

        self.btnProcess = QPushButton(" Process ")
        self.btnProcess.resize(self.btnProcess.sizeHint())
        self.btnProcess.clicked.connect(
            lambda: self.qthRunInThread(
                self.qthProcessCommand, self.leCommand.text()
            )
        )
        self.btnProcess.setToolTip("Execute batch command.")

        self.btnCheckFiles = QPushButton(" Check Files ")
        self.btnCheckFiles.resize(self.btnCheckFiles.sizeHint())
        self.btnCheckFiles.clicked.connect(
            lambda: self.qthRunInThread(self.qthCheckFiles)
        )
        self.btnCheckFiles.setToolTip("Check files for consistency.")

        self.btnShowSourceFiles = QPushButton(" Source Files ")
        self.btnShowSourceFiles.resize(self.btnShowSourceFiles.sizeHint())
        self.btnShowSourceFiles.clicked.connect(
            lambda: self.qthRunInThread(self.qthShowSourceFiles)
        )
        self.btnShowSourceFiles.setToolTip("Files to be processed.")

        self.btnShowCommands = QPushButton(" Commands ")
        self.btnShowCommands.resize(self.btnShowCommands.sizeHint())
        self.btnShowCommands.clicked.connect(
            lambda: self.qthRunInThread(self.qthShowCommands)
        )
        self.btnShowCommands.setToolTip("Commands to be applied.")

        self.btnClearOutputWindow = QPushButton(" Clear Output ")
        self.btnClearOutputWindow.resize(self.btnClearOutputWindow.sizeHint())
        self.btnClearOutputWindow.clicked.connect(self.clearOutputWindow)
        self.btnClearOutputWindow.setToolTip("Erase text in output window.")

        self.btnReset = QPushButton(" Clear/Reset ")
        self.btnReset.resize(self.btnReset.sizeHint())
        self.btnReset.clicked.connect(self.reset)
        self.btnReset.setToolTip("Reset state to work with another batch.")

        self.btnProcess.setEnabled(False)
        self.btnAddQueue.setEnabled(False)
        self.btnProcessQueue.setEnabled(False)
        self.btnClearOutputWindow.setEnabled(False)
        self.btnReset.setEnabled(False)
        self.btnCheckFiles.setEnabled(False)
        self.buttonsState(False)


        self.teOutputWindow = MKVOutputWidget(self)
        self.teOutputWindow.textChanged.connect(self.clearButtonsState)
        self.teOutputWindow.setReadOnly(True)

    def _initLayout(self):

        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        self.btnGrid.addWidget(self.btnPasteClipboard, 0, 0)
        self.btnGrid.addWidget(self.btnPreProcess, 1, 0)
        self.btnGrid.addWidget(self.btnProcess, 1, 1)
        self.btnGrid.addWidget(self.btnAddQueue, 2, 0)
        self.btnGrid.addWidget(self.btnProcessQueue, 2, 1)
        self.btnGrid.addWidget(self.btnShowSourceFiles, 3, 0)
        self.btnGrid.addWidget(self.btnShowCommands, 3, 1)
        self.btnGrid.addWidget(self.btnCheckFiles, 4, 0)
        self.btnGrid.addWidget(self.btnClearOutputWindow, 4, 1)
        self.btnGrid.addWidget(self.btnReset, 5, 0, 1, 2)

        self.btnGroup.setLayout(self.btnGrid)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.lblCommand, 1, 0, 1, 2, Qt.AlignRight)
        self.grid.addWidget(self.leCommand, 1, 2)

        self.grid.addWidget(self.btnGroup, 2, 0, 5, 2)

        self.grid.addWidget(self.teOutputWindow, 2, 2, 10, 1)

        self.setLayout(self.grid)

    @pyqtSlot(int, int)
    def progress(self, unit, total):
        """Update the progress bars"""
        self.parent.progressbar.setValues(unit, total)

    @pyqtSlot(str)
    def updateCommand(self, strCommand):
        """Update command input widget"""

        self.leCommand.clear()
        self.leCommand.setText(strCommand)
        self.leCommand.setCursorPosition(0)

    def qthRunInThread(self, function, *args, **kwargs):
        """
        Pass the function to execute Other args,
        kwargs are passed to the run function
        """
        worker = Worker(function, *args, **kwargs)
        worker.signals.outputmain.connect(self.teOutputWindow.insertText)
        worker.signals.progress.connect(self.progress)
        worker.signals.outputcommand.connect(self.updateCommand)

        # Execute
        self.threadpool.start(worker)

    def clearButtonsState(self):
        """Set clear button state"""
        if self.teOutputWindow.toPlainText() != "":
            self.btnReset.setEnabled(True)
            self.btnClearOutputWindow.setEnabled(True)
        else:
            self.btnReset.setEnabled(False)
            self.btnClearOutputWindow.setEnabled(False)

    def buttonsState(self, bState=None):
        """Change button state"""

        if bState is not None:
            self.btnPreProcess.setEnabled(bState)
            self.btnCheckFiles.setEnabled(bState)
            self.btnShowSourceFiles.setEnabled(bState)
            self.btnShowCommands.setEnabled(bState)

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            self.updateCommand(clip)

    def qthPasteClipboard(self, **kwargs): # pylint: disable=W0613
        """
        Paste clipboard to command QLineEdit
        If not run in a separate thread on macOS does not refresh
        """

        if 'cbOutputCommand' in kwargs:
            cbOutputCommand = kwargs['cbOutputCommand']
        else:
            if self.parent.log:
                MODULELOG.error("FW001: No output command callback function")
            return "No output command callback function"

        clip = QApplication.clipboard().text()

        if clip:
            cbOutputCommand.emit(clip)

        return None

    class ValidateCommand(QValidator):
        """Validate command line entered"""

        def __init__(self, parent=None):
            super(MKVFormWidget.ValidateCommand, self).__init__(parent)

            self.parent = parent

        def validate(self, inputStr, pos):
            """Check regex in bLooksOk"""

            bTest = MKVCommand.bLooksOk(inputStr)

            if bTest:
                self.parent.btnPreProcess.setEnabled(True)
                self.parent.btnProcess.setEnabled(True)
                self.parent.btnAddQueue.setEnabled(True)
                if self.parent.jobs:
                    self.parent.btnProcessQueue.setEnabled(True)
                else:
                    self.parent.btnProcessQueue.setEnabled(False)
                self.parent.btnReset.setEnabled(True)
                if self.parent.parent.log:
                    MODULELOG.debug("FW002: Ok: [%s]", inputStr)
            else:
                self.parent.btnPreProcess.setEnabled(False)
                self.parent.btnProcess.setEnabled(False)
                self.parent.btnAddQueue.setEnabled(False)
                if self.parent.jobs:
                    self.parent.btnProcessQueue.setEnabled(True)
                else:
                    self.parent.btnProcessQueue.setEnabled(False)
                if self.parent.parent.log:
                    MODULELOG.debug("FW003: Not Ok: [%s]", inputStr)

            return (QValidator.Acceptable, inputStr, pos)

    def addQueue(self, **kwargs):
        """Add Command to Work Queue"""

        # Get outputwindow signal function
        kwargsKeys = ['cbOutputCommand', 'cbOutputMain']
        for key in kwargsKeys:
            if not key in kwargs:
                if self.parent.log:
                    MODULELOG.error(
                        "FW007: No output command callback function %s.",
                        key
                    )
                return "No output command callback function"

        cbOutputMain = kwargs['cbOutputMain']
        cbOutputCommand = kwargs['cbOutputCommand']

        cmd = self.leCommand.text()

        bTest = MKVCommand.bLooksOk(cmd)

        if bTest:

            if self.jobs.inQueue(cmd):
                cbOutputMain.emit(
                    "Command already in queue:\n\n{}\n\n".format(cmd),
                    {'color': Qt.blue}
                )
            else:

                jobID, _ = self._addQueue(cmd)

                cbOutputMain.emit(
                    "Command added to queue:\n\nJob {} - {}\n\n".format(jobID, cmd),
                    {'color': Qt.blue}
                )

                # Clear command
                cbOutputCommand.emit("")

                if not self.RUNNING:
                    self.btnProcessQueue.setEnabled(True)

        return "Ok"

    def _addQueue(self, cmd):

        jobStatus = JobStatus()

        jobID = self.jobs.append(cmd, jobStatus.Waiting)
        #self.parent.addJob.emit(jobID, cmd)
        #self.jobs.status(jobID, "Waiting")

        return jobID, cmd

    def qthPreProcess(self, **kwargs):
        """Process command but don't execute for debugging"""

        # Get outputwindow signal function
        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.parent.log:
                MODULELOG.error("FW009: No output callback function")
            return

        if 'enableButtons' in kwargs:
            bEnableButtons = kwargs['enableButtons']
        else:
            bEnableButtons = True

        cmd = self.leCommand.text()

        self.objCommand.command = cmd

        QApplication.processEvents()

        cbOutputMain.emit("Working...\n\n", {'color': Qt.black})

        if self.objCommand:

            cbOutputMain.emit("Getting Files...\n", {'color': Qt.black})

            self.lstBaseFiles = []
            self.lstSourceFiles = []

            _getFiles(
                self.objCommand,
                lbf=self.lstBaseFiles,
                lsf=self.lstSourceFiles,
                clear=True,
                log=True
            )

            if not self.objCommand:
                cbOutputMain.emit(
                    "\n" + self.objCommand.strError,
                    {'color': Qt.red}
                )

            cbOutputMain.emit("\nDone.\n\n\n", {'color': Qt.black})

            if bEnableButtons:
                self.buttonsState(True)

        else:

            cbOutputMain.emit("Error processing command ...\n", {'color': Qt.red})
            cbOutputMain.emit(self.objCommand.strError + "\n\n", {'color': Qt.red})

    def qthCheckFiles(self, **kwargs):
        """Check file structure against primary source file"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.parent.log:
                MODULELOG.error("FW010: No output callback function")
            return "No output callback function"

        cbOutputMain.emit("Checking files...\n\n", {'color': Qt.black})

        if self.lstSourceFiles:

            for lstFiles in self.lstSourceFiles:
                self.objCommand.setFiles(lstFiles)
                if _bVerifyStructure(self.lstBaseFiles, lstFiles, self.parent.log):
                    cbOutputMain.emit(
                        "Structure looks OK:\n" \
                        + str(lstFiles) + "\n\n",
                        {'color': Qt.darkGreen}
                    )
                else:
                    cbOutputMain.emit(
                        "Error: In structure\n" \
                        + str(lstFiles) \
                        + "\n\n",
                        {'color': Qt.red}
                    )

        cbOutputMain.emit("\n", {'color': Qt.black})

        return None

    def qthShowSourceFiles(self, **kwargs):
        """List the source files found"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.parent.log:
                MODULELOG.error("FW011: No output callback function")
            return "No output callback function"

        cbOutputMain.emit(
            "Base Files:\n\n" \
            + str(self.lstBaseFiles) \
            + "\n\nSource Files:\n\n",
            {'color': Qt.black}
        )

        if self.lstSourceFiles:
            for lstFiles in self.lstSourceFiles:
                cbOutputMain.emit(str(lstFiles) + "\n\n", {'color': Qt.black})
        else:
            if not self.objCommand:
                cbOutputMain.emit(
                    "\n" + self.objCommand.strError + "\n\n",
                    {'color': Qt.red}
                )

        cbOutputMain.emit("\n", {'color': Qt.black})

        return None

    def qthShowCommands(self, **kwargs):
        """List the commands to be executed"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.parent.log:
                MODULELOG.error("FW012: No output callback function")
            return "No output callback function"

        cbOutputMain.emit(
            "Shell:\n\n" \
            + self.objCommand.strShellcommand \
            + "\n\n",
            {'color': Qt.black}
        )
        cbOutputMain.emit(
            "Command Template:\n\n" \
            + str(self.objCommand.lstCommandTemplate) \
            + "\n\nCommands:\n\n",
            {'color': Qt.black}
        )
        if self.lstSourceFiles:
            for lstFiles in self.lstSourceFiles:
                self.objCommand.setFiles(lstFiles)
                cbOutputMain.emit(
                    str(self.objCommand.lstProcessCommand),
                    {'color': Qt.black}
                )
        else:
            if not self.objCommand:
                cbOutputMain.emit(
                    "\n" + self.objCommand.strError + "\n\n",
                    {'color': Qt.red}
                )

        cbOutputMain.emit("\n", {'color': Qt.black})

        return None

    def clearOutputWindow(self):
        """Clear the QTextExit widget"""

        result = QMessageBox.question(
            self,
            "Confirm Clear...",
            "Clear output window?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self.teOutputWindow.clear()
            self.btnClearOutputWindow.setEnabled(False)

    def reset(self):
        """Reset values to start over"""

        result = QMessageBox.question(
            self,
            "Confirm Reset...",
            "Reset and clear output?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self._initHelper()

            self.buttonsState(False)
            self.btnProcess.setEnabled(False)
            self.btnPasteClipboard.setEnabled(True)
            self.btnAddQueue.setEnabled(False)
            self.teOutputWindow.clear()
            self.parent.outputQueueWidget.clear()
            self.parent.outputErrorWidget.clear()
            self.parent.jobsWidget.clearTable()
            self.leCommand.clear()
            self.leCommand.setFocus()
            _getFiles(clear=True, log=self.parent.log)
            self.parent.progressbar.setValues(0, 0)

    def qthProcessCommand(self, command=None, **kwargs):
        """Main worker function will process the commands"""

        for key in ['cbOutputCommand', 'cbOutputMain', 'cbProgress']:
            if not key in kwargs:
                if self.parent.log:
                    MODULELOG.error(
                        "FW013: No output command callback function %s.",
                        key
                    )
                return "No output command callback function"

        currentJob = CurrentJob()

        currentJob.outputMain, currentJob.progressBar, \
        currentJob.outputJobMain, currentJob.outputJobError = \
            kwargs['cbOutputMain'], kwargs['cbProgress'], \
            self.jobs.outputJob, self.jobs.outputError

        if not self.RUNNING:

            self.btnProcessQueue.setEnabled(False)

            if command:
                # This is Proccess button request use for TODO:immediate action

                jobID, _ = self._addQueue(command)

                currentJob.outputMain.emit(
                    "Command added to queue:\n\nJob {} - {}\n\n".format(jobID, command),
                    {'color': Qt.blue}
                )

                # Clear command line
                kwargs['cbOutputCommand'].emit("")

            if not self.jobs:
                currentJob.outputMain.emit("\nNothing on Queue.\n", {'color': Qt.blue})
                return "Queue empty"

            self.RUNNING = True  # pylint: disable=C0103

        else:
            currentJob.outputMain.emit("\nProcessing Queue.\n", {'color': Qt.blue})
            return "RUNNING"

        MKVCommand.log = self.parent.log

        currentJob.outputJobMain, \
        currentJob.outputJobError = \
            self.jobs.outputJob, self.jobs.outputError

        workFiles = WorkFiles()

        while self.jobs:

            currentJob.jobID, currentJob.command = self.jobs.popLeft()

            if currentJob.command:
                objCommand = MKVCommand(currentJob.command)
                self.jobs.status(currentJob.jobID, JobStatus.Running)
            else:
                # Skip empty command
                self.jobs.status(currentJob.jobID, JobStatus.Error)
                continue

            currentJob.outputMain.emit(
                "\n\nWorking on Command:\n" \
                + "Job " + str(currentJob.jobID) + " - " \
                + currentJob.command \
                + "\n\n",
                {'color': Qt.blue}
            )

            currentJob.outputJobMain(
                currentJob.jobID,
                "\n\n**********\nWorking on Command:\n" \
                + "Job " + str(currentJob.jobID) + " - " \
                + currentJob.command \
                + "\n**********\n\n",
                {'color': Qt.blue}
            )

            workFiles.clear()

            _getFiles(objCommand, lbf=workFiles.baseFiles, lsf=workFiles.sourceFiles,
                      log=self.parent.log)

            if not objCommand:
                currentJob.outputMain.emit(
                    "\n" + objCommand.strError,
                    {'color': Qt.red}
                )

                currentJob.outputJobMain(
                    currentJob.jobID,
                    "\n" + objCommand.strError,
                    {'color': Qt.red}
                )

                currentJob.outputJobError(
                    currentJob.jobID,
                    "\n" + objCommand.strError,
                    {'color': Qt.red}
                )


            if self.parent.log:
                MODULELOG.info("FW016: Base files in Process: %s",
                               str(workFiles.baseFiles))
                MODULELOG.info("FW017: Source files in Process: %s",
                               str(workFiles.sourceFiles))

            if workFiles.sourceFiles:

                nTotal = len(workFiles.sourceFiles) * 100
                lstTotal = [0, nTotal]

                # Set the total for progressbar to increase gradually
                self.parent.progressbar.pbBarTotal.setMaximum(nTotal)
                # Change to output queue tab
                #self.parent.tabs.setCurrentIndex(2)

                for lstFiles in workFiles.sourceFiles:

                    if self.controlQueue is not None:
                        if not self.controlQueue.empty():
                            request = self.controlQueue.get()
                            if request == JobStatus.Abort:
                                break

                    objCommand.setFiles(lstFiles)

                    if _bVerifyStructure(workFiles.baseFiles, lstFiles, self.parent.log,
                                         currentJob):
                        currentJob.outputJobMain(
                            currentJob.jobID,
                            "\n\nCommand:\n" \
                            + str(objCommand.lstProcessCommand) \
                            + "\n\n",
                            {'color': Qt.blue}
                        )
                        _runCommand(
                            objCommand.lstProcessCommand,
                            currentJob,
                            lstTotal,
                            self.parent.log
                        )
                    else:
                        lstTotal[0] += 100

                currentJob.progressBar.emit(0, nTotal)

                currentStatus = self.jobs.status(currentJob.jobID)

                if currentStatus == JobStatus.Abort:
                    self.jobs.status(int(currentJob.jobID), JobStatus.Aborted)
                    currentJob.outputJobMain(
                        currentJob.jobID, "\n\nJob {} - Aborted.\n".format(currentJob.jobID),
                        {'color': Qt.blue}
                    )
                else:
                    self.jobs.status(int(currentJob.jobID), JobStatus.Done)
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "\n\nJob {} - Done.\n".format(currentJob.jobID),
                        {'color': Qt.blue}
                    )

            else:

                self.jobs.status(currentJob.jobID, JobStatus.Error)

        self.RUNNING = False

        return None


def _getBaseFiles(objCommand, log=False):

    lstBaseFiles = []

    if objCommand and objCommand.lstObjFiles:

        # list of base source files the ones received on command line
        lstBaseFiles = \
            [x.fullPathName for x in objCommand.lstObjFiles]

    else:
        if log:
            MODULELOG.error("FW018: Base files reading error")

    return lstBaseFiles

def _bCheckLenOfLists(lstLists, lstTypeTotal):

    intTmp = None
    bReturn = True

    for lstTmp in lstLists:

        lstTypeTotal.append([str(len(lstTmp)), os.path.splitext(lstTmp[0])[1]])

        if not intTmp:
            intTmp = len(lstTmp)
        else:
            if len(lstTmp) != intTmp:
                if bReturn:
                    bReturn = False

    return bReturn

def _getSourceFiles(objCommand, log=False):

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

        if _bCheckLenOfLists(lstMKVFiles, lstTypeTotal):

            # Join all source files in a list of lists each element
            # have all source files in the order found
            # That is the names are not used the order in the directories is
            for i in range(len(lstMKVFiles[0])):
                lstSourceFiles.append([x[i] for x in lstMKVFiles])
        else:
            objCommand.bRaiseError = True
            error = "FW019: List of files total don't match."
            objCommand.strError = error + "\n\n"
            if log:
                MODULELOG.error("FW019: List of files total don't match")
            for lstTmp in lstTypeTotal:
                error = lstTmp[0] + " - " + lstTmp[1]
                objCommand.strError = objCommand.strError + error + "\n"
                if log:
                    MODULELOG.error("FW020: File(s): %s", error)

    return lstSourceFiles

def _bVerifyStructure(lstBaseFiles, lstFiles, log=False, currentJob=None):

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
def _getFiles(objCommand=None, lbf=None, lsf=None, clear=False, log=False):
    """Get the list of files to be worked on in thread safe manner"""

    with QMutexLocker(MUTEX):
        if clear:
            _getFiles.strCommand = ""
            _getFiles.lstBaseFiles = []
            _getFiles.lstSourceFiles = []

        if objCommand is not None:
            if objCommand.strShellcommand != _getFiles.strCommand:
                # Information not in cache.
                _getFiles.strCommand = objCommand.strShellcommand
                _getFiles.lstBaseFiles = _getBaseFiles(objCommand, log=log)
                _getFiles.lstSourceFiles = _getSourceFiles(objCommand, log=log)
            else:
                if log:
                    MODULELOG.info("FW021: Hit cached information.")

            # lbf and lsf are mutable pass information back here
            # this approach should make it thread safe so
            # qhtProcess command can work on a queue
            if lbf is not None:
                lbf.extend(_getFiles.lstBaseFiles)

            if lsf is not None:
                lsf.extend(_getFiles.lstSourceFiles)

        if log:
            MODULELOG.info("FW022: Base files: %s", str(_getFiles.lstBaseFiles))
            MODULELOG.info("FW023: Source files: %s", str(_getFiles.lstSourceFiles))

def _runCommand(command, currentJob, lstTotal, log=False):
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
        MODULELOG.info("FW024: mkvmerge rc=%d - %s", rc, command)

    return rc
