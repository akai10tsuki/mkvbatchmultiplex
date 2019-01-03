#!/usr/bin/env python3

"""
MKVFormWidget:

Main form

LOG FW025
"""

import logging
import platform
#import time
from queue import Queue

from PySide2.QtCore import Qt, QTimer, Signal, Slot
from PySide2.QtGui import QValidator
from PySide2.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
                               QLineEdit, QMessageBox, QPushButton,
                               QWidget)

import mkvbatchmultiplex.qththreads as threads
import mkvbatchmultiplex.utils as utils

from mkvbatchmultiplex.mediafileclasses import MKVCommand

from .MKVOutputWidget import MKVOutputWidget
from .MKVJobsTableWidget import JobStatus


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CurrentJob: # pylint: disable=R0903
    """Helper class for working with a job"""

    def __init__(self):

        self.jobID = None
        self.status = None
        self.command = None
        self.outputMain = None
        self.outputJobMain = None
        self.outputJobError = None
        self.progressBar = None


class WorkerSignals(threads.WorkerSignals):
    """Additional signals for QRunables"""

    progress = Signal(int, int)
    outputmain = Signal(str, dict)
    outputcommand = Signal(str)


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

    def __init__(self, parent, qthThread, jobs, ctrlQueue, log=False):
        super(MKVFormWidget, self).__init__(parent)

        self.parent = parent
        self.log = log
        self.threadpool = qthThread
        self.jobs = jobs
        self.controlQueue = ctrlQueue
        self.controlRunCommand = Queue()
        self.objCommand = MKVCommand()
        self.lstSourceFiles = []
        self.lstBaseFiles = []

        self._initControls()
        self._initLayout()

        self.requestedClose = False
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.watchJobs)
        self.timer.start()

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

        self.btnAnalysis = QPushButton(" Analysis ")
        self.btnAnalysis.resize(self.btnAnalysis.sizeHint())
        self.btnAnalysis.clicked.connect(
            lambda: self.qthRunInThread(self.qthAnalysis)
        )
        self.btnAnalysis.setToolTip(
            "Print analysis of command line."
        )
        self.leCommand.textChanged.connect(self.analysisButtonsState)

        self.btnAddQueue = QPushButton(" Add Job ")
        self.btnAddQueue.resize(self.btnAddQueue.sizeHint())
        self.btnAddQueue.clicked.connect(
            lambda: self.qthRunInThread(self.addQueue)
        )
        self.btnAddQueue.setToolTip(
            "Add command to job queue."
        )

        self.btnProcessQueue = QPushButton(" Process Jobs ")
        self.btnProcessQueue.resize(self.btnProcessQueue.sizeHint())
        self.btnProcessQueue.clicked.connect(
            lambda: self.qthRunInThread(self.qthProcessCommand)
        )
        self.btnProcessQueue.setToolTip("Execute commands on job queue.")

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


        self.buttonsState(False)
        self.btnAnalysis.setEnabled(False)
        self.btnProcessQueue.setEnabled(False)
        self.btnClearOutputWindow.setEnabled(False)
        self.btnReset.setEnabled(False)

        self.teOutputWindow = MKVOutputWidget(self)
        self.teOutputWindow.textChanged.connect(self.clearButtonsState)
        self.teOutputWindow.setReadOnly(True)

    def _initLayout(self):

        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        self.btnGrid.addWidget(self.btnPasteClipboard, 0, 0)
        self.btnGrid.addWidget(self.btnAnalysis, 1, 0)
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

    @Slot(int, int)
    def progress(self, unit, total):
        """Update the progress bars"""
        self.parent.progressbar.setValues(unit, total)

    @Slot(str)
    def updateCommand(self, strCommand):
        """Update command input widget"""

        self.leCommand.clear()
        self.leCommand.setText(strCommand)
        self.leCommand.setCursorPosition(0)

    def watchJobs(self):
        """
        Enable <Process Jobs> button when needed
        Hack until job queue is reworked
        """

        #while True:
        if self.jobs.jobsAreWaiting():
            tmpNum = self.threadpool.activeThreadCount()

            if tmpNum == 0:
                self.jobs.requeueWaiting()
                self.btnProcessQueue.setEnabled(True)

        js = self.jobs.jobsStatus()

        if js == JobStatus.Aborted:
            self.parent.close()

        #time.sleep(2)

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

    def analysisButtonsState(self):
        """Set clear button state"""
        if self.leCommand.text() != "":
            self.btnAnalysis.setEnabled(True)
        else:
            self.btnAnalysis.setEnabled(False)

    def buttonsState(self, bState=None):
        """Change button state"""

        if bState is not None:
            #self.btnCheckFiles.setEnabled(bState)
            #self.btnShowSourceFiles.setEnabled(bState)
            #self.btnShowCommands.setEnabled(bState)

            self.btnShowSourceFiles.setEnabled(bState)
            self.btnShowCommands.setEnabled(bState)
            self.btnCheckFiles.setEnabled(bState)
            self.btnProcess.setEnabled(bState)
            self.btnAddQueue.setEnabled(bState)

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
            if self.log:
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
                self.parent.objCommand.command = inputStr

                self.parent.buttonsState(True)

                self.parent.btnReset.setEnabled(True)

                if self.parent.log:
                    MODULELOG.debug("FW002: Command Ok: [%s]", inputStr)
            else:
                self.parent.buttonsState(False)

                if self.parent.log:
                    MODULELOG.debug("FW003: Command not Ok: [%s]", inputStr)

            return (QValidator.Acceptable, inputStr, pos)

    def qthAnalysis(self, **kwargs):
        """List the source files found"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("FW011: No output callback function")
            return "No output callback function"

        lstAnalysis = []
        cmd = self.leCommand.text()

        MKVCommand.bLooksOk(cmd, lstAnalysis)

        cbOutputMain.emit("\nAnalysis of command line:\n\n", {})

        if lstAnalysis:
            for e in lstAnalysis:
                i = e.find(r"ok")
                if i > 0:
                    cbOutputMain.emit("{}\n".format(e), {'color': Qt.darkGreen})
                else:
                    cbOutputMain.emit("{}\n".format(e), {'color': Qt.red})

        cbOutputMain.emit("\n", {})

        return None

    def addQueue(self, **kwargs):
        """Add Command to Work Queue"""

        # Get outputwindow signal function
        kwargsKeys = ['cbOutputCommand', 'cbOutputMain']
        for key in kwargsKeys:
            if not key in kwargs:
                if self.log:
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

                tmpNum = self.threadpool.activeThreadCount()

                if tmpNum == 0:
                    self.btnProcessQueue.setEnabled(True)

        return "Ok"

    def _addQueue(self, cmd):

        jobStatus = JobStatus()

        jobID = self.jobs.append(cmd, jobStatus.Waiting)

        self.parent.jobsLabel[0] = len(self.jobs)

        return jobID, cmd

    def qthShowSourceFiles(self, **kwargs):
        """List the source files found"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("FW011: No output callback function")
            return "No output callback function"

        cbOutputMain.emit(
            "Base Files:\n\n" \
            + str(self.objCommand.basefiles) \
            + "\n\nSource Files:\n\n",
            {}
        )

        if self.objCommand:
            for _, _, lstFiles in self.objCommand:
                cbOutputMain.emit(str(lstFiles) + "\n\n", {})
        else:
            cbOutputMain.emit(
                "\n" + self.objCommand.error + "\n\n",
                {'color': Qt.red}
            )

        cbOutputMain.emit("\n", {})

        return None

    def qthShowCommands(self, **kwargs):
        """List the commands to be executed"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("FW012: No output callback function")
            return "No output callback function"

        cbOutputMain.emit(
            "Shell:\n\n" \
            + self.objCommand.command \
            + "\n\n",
            {}
        )
        cbOutputMain.emit(
            "Command Template:\n\n" \
            + str(self.objCommand.template) \
            + "\n\nCommands:\n\n",
            {}
        )

        if self.objCommand:
            for command, _, _ in self.objCommand:
                cbOutputMain.emit(
                    str(command) + "\n\n",
                    {}
                )
        else:
            cbOutputMain.emit(
                "\n" + self.objCommand.error + "\n\n",
                {'color': Qt.red}
            )

        cbOutputMain.emit("\n", {})

        return None

    def qthCheckFiles(self, **kwargs):
        """Check file structure against primary source file"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("FW010: No output callback function")
            return "No output callback function"

        cbOutputMain.emit("Checking files...\n\n", {})

        if self.objCommand:

            for _, basefiles, sourcefiles in self.objCommand:

                if utils.bVerifyStructure(basefiles, sourcefiles, self.log):
                    cbOutputMain.emit(
                        "Structure looks OK:\n" \
                        + str(sourcefiles) + "\n\n",
                        {'color': Qt.darkGreen}
                    )
                else:
                    cbOutputMain.emit(
                        "Error: In structure\n" \
                        + str(sourcefiles) \
                        + "\n\n",
                        {'color': Qt.red}
                    )

        cbOutputMain.emit("\n", {})

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
            self.parent.progressbar.setValues(0, 0)

            jobsLabelValues = self.parent.jobsLabel.values

            jobsLabelValues[0] = len(self.jobs)

            self.parent.jobsLabel.setValues(jobsLabelValues)

    def qthProcessCommand(self, command=None, **kwargs):
        """Main worker function will process the commands"""

        for key in ['cbOutputCommand', 'cbOutputMain', 'cbProgress']:
            if not key in kwargs:
                if self.log:
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
            self.jobs.jobsStatus(JobStatus.Running)

        else:
            currentJob.outputMain.emit("\nProcessing Queue.\n", {'color': Qt.blue})
            return "RUNNING"

        MKVCommand.log = self.log

        currentJob.outputJobMain, \
        currentJob.outputJobError = \
            self.jobs.outputJob, self.jobs.outputError

        result = None

        objCommand = MKVCommand()

        while self.jobs:

            currentJob.jobID, currentJob.command = self.jobs.popLeft()

            status = self.jobs.status(currentJob.jobID)

            if status != JobStatus.Waiting:
                currentJob.outputMain.emit(
                    "\n\nJob - {0} with {1} status skipping.".format(str(currentJob.jobID), status),
                    {'color': Qt.blue}
                )

                currentJob.outputJobMain(
                    currentJob.jobID,
                    "\n\n**********\nSkip requested on Command:\n" \
                    + "Job " + str(currentJob.jobID) + " - " \
                    + currentJob.command \
                    + "\n**********\n\n",
                    {'color': Qt.blue}
                )
                continue

            if currentJob.command:
                objCommand.command = currentJob.command
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

            if not objCommand:
                currentJob.outputMain.emit(
                    "\n" + objCommand.error,
                    {'color': Qt.red}
                )

                currentJob.outputJobMain(
                    currentJob.jobID,
                    "\n" + objCommand.error,
                    {'color': Qt.red}
                )

                currentJob.outputJobError(
                    currentJob.jobID,
                    "\n" + objCommand.error,
                    {'color': Qt.red}
                )

                if self.log:
                    MODULELOG.info("FW016: Base files in Process: %s",
                                   str(objCommand.basefiles))
                    MODULELOG.info("FW017: Source files in Process: %s",
                                   str(objCommand.sourcefiles))

            if objCommand:

                self.parent.jobsLabel[1] = currentJob.jobID
                self.parent.jobsLabel[3] = len(objCommand)

                currentJob.jobsLabelValues = self.parent.jobsLabel.values

                nTotal = len(objCommand) * 100
                nFile = 0
                lstTotal = [0, nTotal]

                # Set the total for progressbar to increase gradually
                self.parent.progressbar.pbBarTotal.setMaximum(nTotal)
                # Change to output queue tab
                #self.parent.tabs.setCurrentIndex(2)

                for command, basefiles, sourcefiles in objCommand:

                    nFile += 1

                    currentStatus = self.jobs.status(currentJob.jobID)

                    if currentStatus == JobStatus.Abort:
                        break

                    if self.controlQueue is not None:
                        if not self.controlQueue.empty():
                            request = self.controlQueue.get()
                            if request == JobStatus.Abort:
                                self.jobs.status(currentJob.jobID, JobStatus.Aborted)
                                self.jobs.clear()
                                self.jobs.abortAll()
                                self.jobs.jobsStatus(JobStatus.Aborted)
                                self.RUNNING = False
                                return JobStatus.Aborted

                    bStructureOk = False

                    try:
                        bStructureOk = utils.bVerifyStructure(
                            basefiles,
                            sourcefiles,
                            self.log,
                            currentJob
                        )
                    except OSError as e:
                        currentJob.outputMain.emit(
                            "\n\nMediaInfo not found.\n\n",
                            {'color': Qt.red}
                        )
                        # Error unable to continue
                        self.jobs.status(currentJob.jobID, JobStatus.Error)
                        self.jobs.clear()
                        self.jobs.abortAll()
                        self.jobs.jobsStatus(JobStatus.Error)
                        return e

                    if bStructureOk:
                        currentJob.outputJobMain(
                            currentJob.jobID,
                            "\n\nCommand:\n" \
                            + str(command) \
                            + "\n\n",
                            {'color': Qt.blue}
                        )
                        self.parent.jobsLabel[2]
                        utils.runCommand(
                            command,
                            currentJob,
                            lstTotal,
                            self.log
                        )
                    else:
                        self.parent.jobsLabel[4] += 1
                        lstTotal[0] += 100


                # End Processing

                currentJob.progressBar.emit(0, nTotal)

                currentStatus = self.jobs.status(currentJob.jobID)

                if currentStatus == JobStatus.Abort:
                    self.jobs.status(currentJob.jobID, JobStatus.Aborted)
                    currentJob.outputJobMain(
                        currentJob.jobID, "\n\nJob {} - Aborted.\n".format(currentJob.jobID),
                        {'color': Qt.blue}
                    )
                else:
                    self.jobs.status(currentJob.jobID, JobStatus.Done)
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "\n\nJob {} - Done.\n".format(currentJob.jobID),
                        {'color': Qt.blue}
                    )

            else:

                self.jobs.status(currentJob.jobID, JobStatus.Error)

        self.RUNNING = False
        self.jobs.jobsStatus(JobStatus.Done)

        return result
