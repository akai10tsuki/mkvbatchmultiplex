"""
MKVCommandWidget:

Command input widget
"""

#LOG MCW0013

import logging
import platform

from queue import Queue
from pathlib import Path

from PySide2.QtCore import Qt, QTimer, Signal, Slot
from PySide2.QtGui import QValidator
from PySide2.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLabel,
                               QLineEdit, QMessageBox, QPushButton, QWidget)

import vsutillib.mkv as mkv

from .. import qththreads as threads
from .. import utils

#from ..mediafileclasses import MKVCommand
from ..jobs import JobStatus
from .MKVOutputWidget import MKVOutputWidget

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVCommandWidget(QWidget):
    """Central widget"""
    # pylint: disable=too-many-instance-attributes
    # Defining elements of a GUI

    __log = False

    setOutputFileSignal = Signal(object)

    @classmethod
    def classLog(cls, setLogging=None):
        """get/set global logging"""

        if setLogging is None:
            return cls.__log
        elif isinstance(setLogging, bool):
            cls.__log = setLogging

    def __init__(self, parent, qthThread, jobs, jobCtrlQueue, jobSpCtrlQueue,
                 renameWidget):
        super(MKVCommandWidget, self).__init__(parent)

        mkv.MKVCommand.log = self.log
        mkv.VerifyStructure.log = self.log

        self.parent = parent
        self.threadpool = qthThread
        self.jobs = jobs
        self.controlQueue = jobCtrlQueue
        self.spControlQueue = jobSpCtrlQueue
        self.controlRunCommand = Queue()
        self.objCommand = None

        self._initControls()
        self._initLayout()

        #self.requestedClose = False
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.watchJobs)
        self.timer.start()
        self.renameWidget = renameWidget

        self.renameWidget.connectToSetOutputFile(self.setOutputFileSignal)
        self.renameWidget.applyFileRenameSignal.connect(self._applyRename)

    def _initHelper(self):
        self.objCommand = None

    def _initControls(self):
        """Controls for Widget"""

        self.lblCommand = QLabel("MKVMERGE Command Line")

        # Command line input mkvtoolnix-gui: Multiplexer->Show command line
        self.leCommand = QLineEdit()
        self.leCommand.setClearButtonEnabled(True)
        validator = ValidateCommand(self)
        self.leCommand.setValidator(validator)

        self.btnPasteClipboard = QPushButton(" Paste Clipboard ")
        self.btnPasteClipboard.resize(self.btnPasteClipboard.sizeHint())
        if platform.system() != "Linux":
            #macOS will not update if a thread is not used
            #linux - ubuntu won't work with this the first click fails
            #    from there on it work
            #windows - work

            self.btnPasteClipboard.clicked.connect(lambda: self.qthRunInThread(
                self.qthPasteClipboard))
        else:
            #linux - ubuntu only refresh correctly this way
            #macOS - refresh doesn't work must use keyboard arrows to refresh
            #windows - work

            self.btnPasteClipboard.clicked.connect(self.pasteClipboard)
        self.btnPasteClipboard.setToolTip(
            "Paste copy of <b>mkvtoolnix-gui</b> Show command line")

        self.btnAnalysis = QPushButton(" Analysis ")
        self.btnAnalysis.resize(self.btnAnalysis.sizeHint())
        self.btnAnalysis.clicked.connect(lambda: self.qthRunInThread(
            self.qthAnalysis))
        self.btnAnalysis.setToolTip("Print analysis of command line.")
        self.leCommand.textChanged.connect(self.analysisButtonsState)

        self.btnAddQueue = QPushButton(" Add Job ")
        self.btnAddQueue.resize(self.btnAddQueue.sizeHint())
        self.btnAddQueue.clicked.connect(lambda: self.qthRunInThread(self.
                                                                     addQueue))
        self.btnAddQueue.setToolTip("Add command to job queue.")

        self.btnProcessQueue = QPushButton(" Process Jobs ")
        self.btnProcessQueue.resize(self.btnProcessQueue.sizeHint())
        self.btnProcessQueue.clicked.connect(lambda: self.qthRunInThread(
            self.qthProcessCommand))
        self.btnProcessQueue.setToolTip("Execute commands on job queue.")

        self.btnProcess = QPushButton(" Process ")
        self.btnProcess.resize(self.btnProcess.sizeHint())
        self.btnProcess.clicked.connect(lambda: self.qthRunInThread(
            self.qthProcessCommand, self.objCommand))
        self.btnProcess.setToolTip("Execute batch command.")

        self.btnCheckFiles = QPushButton(" Check Files ")
        self.btnCheckFiles.resize(self.btnCheckFiles.sizeHint())
        self.btnCheckFiles.clicked.connect(lambda: self.qthRunInThread(
            self.qthCheckFiles))
        self.btnCheckFiles.setToolTip("Check files for consistency.")

        self.btnShowSourceFiles = QPushButton(" Source Files ")
        self.btnShowSourceFiles.resize(self.btnShowSourceFiles.sizeHint())
        self.btnShowSourceFiles.clicked.connect(lambda: self.qthRunInThread(
            self.qthShowSourceFiles))
        self.btnShowSourceFiles.setToolTip("Files to be processed.")

        self.btnShowCommands = QPushButton(" Commands ")
        self.btnShowCommands.resize(self.btnShowCommands.sizeHint())
        self.btnShowCommands.clicked.connect(lambda: self.qthRunInThread(
            self.qthShowCommands))
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

        self.textOutputWindow = MKVOutputWidget(self)
        self.textOutputWindow.textChanged.connect(self.clearButtonsState)
        self.textOutputWindow.setReadOnly(True)

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

        self.grid.addWidget(self.textOutputWindow, 2, 2, 10, 1)

        self.setLayout(self.grid)

    @property
    def log(self):
        """return value of self._log"""
        return self.__log

    @log.setter
    def log(self, value):
        """
        update self._log
        and utility functions too
        """
        if isinstance(value, bool):
            self.log = value
            mkv.MKVCommand.classLog(self.log)
            mkv.VerifyStructure.classLog(self.log)

    @staticmethod
    def setLogging(value):
        """
        update self._log
        and utility functions too
        """
        MKVCommandWidget.log = value
        mkv.MKVCommand.log = value
        mkv.VerifyStructure.log = value

    @Slot(list)
    def _applyRename(self, renameFiles):

        if self.objCommand:
            self.objCommand.renameOutputFiles(renameFiles)

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

    @Slot(int, object)
    def updateJobsLabel(self, index, value):
        """Update Jobs Label"""

        self.parent.jobsLabel[index] = value

    def watchJobs(self):
        """
        Enable <Process Jobs> button when needed
        Hack until job queue is reworked
        """

        #while True:
        if self.jobs.jobsAreWaiting():

            jobsCurrentStatus = self.jobs.jobsStatus()

            if jobsCurrentStatus == JobStatus.Blocked:
                self.btnProcess.setEnabled(False)
                self.btnProcessQueue.setEnabled(False)

            else:
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
        worker.signals.outputmain.connect(self.textOutputWindow.insertText)
        worker.signals.progress.connect(self.progress)
        worker.signals.outputcommand.connect(self.updateCommand)
        worker.signals.jobslabel.connect(self.updateJobsLabel)

        # Execute
        self.threadpool.start(worker)

    def clearButtonsState(self):
        """Set clear button state"""
        if self.textOutputWindow.toPlainText() != "":
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
            if self.jobs.jobsStatus() == JobStatus.Blocked:
                self.btnCheckFiles.setEnabled(False)
                self.btnProcess.setEnabled(False)
                self.btnAddQueue.setEnabled(False)
            else:
                self.btnCheckFiles.setEnabled(bState)
                self.btnProcess.setEnabled(bState)
                self.btnAddQueue.setEnabled(bState)

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            self.updateCommand(clip)

    def qthPasteClipboard(self, **kwargs):  # pylint: disable=W0613
        """
        Paste clipboard to command QLineEdit
        If not run in a separate thread on macOS does not refresh
        """

        if 'cbOutputCommand' in kwargs:
            cbOutputCommand = kwargs['cbOutputCommand']
        else:
            if self.log:
                MODULELOG.error("MCW0001: No output command callback function")
            return "No output command callback function"

        clip = QApplication.clipboard().text()

        if clip:
            cbOutputCommand.emit(clip)

        return None

    def qthAnalysis(self, **kwargs):
        """List the source files found"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("MCW0004: No output callback function")
            return "No output callback function"

        cmd = self.leCommand.text()

        verify = mkv.VerifyMKVCommand(cmd)

        cbOutputMain.emit("Analysis of command line:\n\n", {})

        for e in verify.analysis:
            i = e.find(r"chk:")
            if i >= 0:
                cbOutputMain.emit("{}\n".format(e), {'color': Qt.darkGreen})
            else:
                cbOutputMain.emit("{}\n".format(e), {'color': Qt.red})

        cbOutputMain.emit("\n", {})

        return None

    def addQueue(self, **kwargs):
        """Add Command to Work Queue"""

        if self.jobs.jobsStatus() == JobStatus.Blocked:
            self.btnProcessQueue.setEnabled(True)
            return JobStatus.Blocked

        # Get outputwindow signal function
        kwargsKeys = ['cbOutputCommand', 'cbOutputMain', 'cbJobsLabel']
        for key in kwargsKeys:
            if not key in kwargs:
                if self.log:
                    MODULELOG.error(
                        "MCW0005: No output command callback function %s.",
                        key)
                return "No output command callback function"

        cbOutputMain = kwargs['cbOutputMain']
        cbOutputCommand = kwargs['cbOutputCommand']
        cbJobsLabel = kwargs['cbJobsLabel']

        if self.objCommand:

            cmd = self.objCommand.command

            if self.jobs.inQueue(cmd):
                cbOutputMain.emit(
                    "Command already in queue:\n\n{}\n\n".format(cmd),
                    {'color': Qt.blue})

            else:

                jobID, _ = self._addQueue(self.objCommand, cbJobsLabel)

                cbOutputMain.emit(
                    "Command added to queue:\n\nJob {0} - {1}\n\n".format(
                        jobID, cmd), {'color': Qt.blue})

                # Clear command
                cbOutputCommand.emit("")

                tmpNum = self.threadpool.activeThreadCount()

                if tmpNum == 0:
                    self.btnProcessQueue.setEnabled(True)

        return "Ok"

    def _addQueue(self, objCommmad, callback, appendLeft=False):

        jobStatus = JobStatus()

        if appendLeft:
            jobID = self.jobs.appendLeft(objCommmad, jobStatus.Waiting)
        else:
            jobID = self.jobs.append(objCommmad, jobStatus.Waiting)

        callback.emit(0, len(self.jobs))

        return jobID, objCommmad.command

    def qthShowSourceFiles(self, **kwargs):
        """List the source files found"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("MCW0006: No output callback function")
            return "No output callback function"

        msg = "Base Files:\n\n{}\n\nSource Files:\n\n".format(
            str(self.objCommand.baseFiles))

        cbOutputMain.emit(msg, {})

        if self.objCommand:
            for _, _, lstFiles, dFile, _ in self.objCommand:
                lstFile = []
                for f in lstFiles:
                    lstFile.append(str(f))

                cbOutputMain.emit(
                    str(lstFile) + "\n" + str(dFile) + "\n\n", {})
        else:
            cbOutputMain.emit(self.objCommand.error + "\n\n",
                              {'color': Qt.red})

        cbOutputMain.emit("\n", {})

        return None

    def qthShowCommands(self, **kwargs):
        """List the commands to be executed"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("MCW0007: No output callback function")
            return "No output callback function"

        cbOutputMain.emit("Shell:\n\n{}\n\n".format(self.objCommand.command),
                          {})
        cbOutputMain.emit(
            "Command Template:\n\n{}\n\nCommands:\n\n".format(
                str(self.objCommand.template)), {})

        if self.objCommand:
            for command, _, _, _, _ in self.objCommand:
                cbOutputMain.emit(str(command) + "\n\n", {})
        else:
            cbOutputMain.emit(
                "MCW0008: Error in command construction {}\n\n".format(
                    self.objCommand.error), {'color': Qt.red})

        cbOutputMain.emit("\n", {})

        return None

    def qthCheckFiles(self, **kwargs):
        """Check file structure against primary source file"""

        if 'cbOutputMain' in kwargs:
            cbOutputMain = kwargs['cbOutputMain']
        else:
            if self.log:
                MODULELOG.error("MCW0009: No output callback function")
            return "No output callback function"

        cbOutputMain.emit("Checking files...\n\n", {})

        if self.objCommand:

            verify = mkv.VerifyStructure()

            for _, basefiles, sourcefiles, _, _ in self.objCommand:

                verify.verifyStructure(basefiles, sourcefiles)

                if verify:
                    lstFile = []
                    for f in sourcefiles:
                        lstFile.append(str(f))

                    cbOutputMain.emit(
                        "Structure looks OK:\n" \
                        + str(lstFile) + "\n\n",
                        {'color': Qt.darkGreen}
                    )
                else:
                    cbOutputMain.emit(
                        str(verify) \
                        + "\n\n",
                        {'color': Qt.red}
                    )

        cbOutputMain.emit("\n", {})

        return None

    def clearOutputWindow(self):
        """Clear the QTextExit widget"""

        result = QMessageBox.question(self, "Confirm Clear...",
                                      "Clear output window?",
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)

        if result == QMessageBox.Yes:
            self.textOutputWindow.clear()
            self.btnClearOutputWindow.setEnabled(False)

    def reset(self):
        """Reset values to start over"""

        result = QMessageBox.question(self, "Confirm Reset...",
                                      "Reset and clear output?",
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)

        if result == QMessageBox.Yes:
            self._initHelper()

            self.buttonsState(False)
            self.btnProcess.setEnabled(False)
            self.btnPasteClipboard.setEnabled(True)
            self.btnAddQueue.setEnabled(False)
            self.textOutputWindow.clear()
            self.parent.outputQueueWidget.clear()
            self.parent.outputErrorWidget.clear()
            self.parent.jobsWidget.clearTable()
            self.leCommand.clear()
            self.leCommand.setFocus()
            self.parent.progressbar.setValues(0, 0)

            jobsLabelValues = [0, 0, 0, 0, 0]
            jobsLabelValues[0] = len(self.jobs)

            self.parent.jobsLabel.setValues(jobsLabelValues)

    def qthProcessCommand(self, oCommand=None, **kwargs):
        """Main worker function will process the commands"""

        if self.jobs.jobsStatus() != JobStatus.Running:

            for key in [
                    'cbOutputCommand', 'cbOutputMain', 'cbProgress',
                    'cbJobsLabel'
            ]:
                if not key in kwargs:
                    if self.log:
                        MODULELOG.error(
                            "MCW0010: No output command callback function %s.",
                            key)
                    return "No output command callback function"

            currentJob = CurrentJob()

            (currentJob.outputMain, currentJob.progressBar,
             currentJob.jobsLabel, currentJob.outputJobMain,
             currentJob.outputJobError, currentJob.controlQueue,
             currentJob.spControlQueue) = (kwargs['cbOutputMain'],
                                           kwargs['cbProgress'],
                                           kwargs['cbJobsLabel'],
                                           self.jobs.outputJob,
                                           self.jobs.outputError,
                                           self.controlQueue,
                                           self.spControlQueue)

        if oCommand:
            # This is Proccess button request use for TODO:immediate action add to next job

            jobID, _ = self._addQueue(oCommand,
                                      kwargs['cbJobsLabel'],
                                      appendLeft=True)

            currentJob.outputMain.emit(
                "Command added to queue:\n\nJob {} - {}\n\n".format(
                    jobID, oCommand.command), {'color': Qt.blue})

            # Clear command line
            kwargs['cbOutputCommand'].emit("")

        if self.jobs.jobsStatus() == JobStatus.Running:
            # if RUNNING just add command to que if given
            currentJob.outputMain.emit("\nProcessing Queue.\n",
                                       {'color': Qt.blue})
            return "RUNNING"

        self.btnProcessQueue.setEnabled(False)

        if not self.jobs:
            currentJob.outputMain.emit("\nNothing on Queue.\n",
                                       {'color': Qt.blue})
            return "Queue empty"

        self.jobs.jobsStatus(JobStatus.Running)

        #objCommand = mkv.MKVCommand()
        verify = mkv.VerifyStructure()

        while self.jobs:

            currentJob.jobID, currentJob.command, objCommand = self.jobs.popLeft(
            )

            status = self.jobs.status(currentJob.jobID)

            if status != JobStatus.Waiting:

                msg = "**********\nSkip requested on Command:\nJob {0} - {1}\n**********\n\n"
                msg = msg.format(str(currentJob.jobID), currentJob.command)

                currentJob.outputJobMain(currentJob.jobID, msg,
                                         {'color': Qt.blue})
                continue

            if currentJob.command:
                self.jobs.status(currentJob.jobID, JobStatus.Running)
            else:
                # Skip empty command
                self.jobs.status(currentJob.jobID, JobStatus.Error)
                continue

            msg = "**********\nWorking on Command:\nJob {0} - {1}\n**********\n\n"
            msg = msg.format(str(currentJob.jobID), currentJob.command)

            currentJob.outputJobMain(currentJob.jobID, msg, {'color': Qt.blue})

            if objCommand:

                currentJob.jobsLabel.emit(1, currentJob.jobID)
                currentJob.jobsLabel.emit(3, len(objCommand))

                nTotal = len(objCommand) * 100
                nFile = 0
                lstTotal = [0, nTotal, 0]

                # Set the total for progressbar to increase gradually
                self.parent.progressbar.pbBarTotal.setMaximum(nTotal)
                # Change to output queue tab
                if len(self.jobs) == 1:
                    self.parent.tabs.setCurrentIndex(2)

                for cmd, basefiles, sourcefiles, _, _ in objCommand:

                    currentStatus = self.jobs.status(currentJob.jobID)

                    if currentStatus == JobStatus.AbortJob:
                        break

                    if self.controlQueue is not None:
                        if not self.controlQueue.empty():
                            request = self.controlQueue.get()

                            if request == JobStatus.AbortJob:
                                self.jobs.status(currentJob.jobID,
                                                 JobStatus.AbortJob)
                                break

                            if request == JobStatus.AbortJobError:
                                self.jobs.status(currentJob.jobID,
                                                 JobStatus.Error)
                                p = Path(objCommand[nFile - 1][3])
                                if p.is_file():
                                    p.unlink()
                                break

                            if request in [
                                    JobStatus.Abort, JobStatus.AbortForced
                            ]:
                                if request == JobStatus.AbortForced:
                                    p = Path(objCommand[nFile - 1][3])
                                    if p.is_file():
                                        p.unlink()
                                self.jobs.status(currentJob.jobID,
                                                 JobStatus.Aborted)
                                self.jobs.clear()
                                self.jobs.abortAll()
                                self.jobs.jobsStatus(JobStatus.Aborted)
                                return JobStatus.Aborted

                    currentJob.outputJobMain(
                        currentJob.jobID, "Command:\n{}\n\n".format(str(cmd)),
                        {'color': Qt.blue})

                    bStructureOk = False

                    try:
                        verify.verifyStructure(basefiles, sourcefiles)
                        bStructureOk = verify.isOk

                        if not verify.isOk:
                            _outputError(currentJob, str(verify))

                    except OSError as e:

                        msg = "MediaInfo not found.\n{}\n\n".format(e)
                        currentJob.outputJobMain(currentJob.jobID, msg,
                                                 {'color': Qt.red})
                        # Error unable to continue
                        self.jobs.status(currentJob.jobID, JobStatus.Error)
                        self.jobs.clear()
                        self.jobs.abortAll()
                        self.jobs.jobsStatus(JobStatus.Error)
                        # May be rude but is show stopper
                        self.parent.tabs.setCurrentIndex(2)

                        return e

                    if bStructureOk:
                        nFile += 1
                        currentJob.jobsLabel.emit(2, nFile)
                        utils.runCommand(cmd, currentJob, lstTotal, self.log)
                        currentJob.jobsLabel.emit(
                            4, self.parent.jobsLabel[4] + lstTotal[2])
                        lstTotal[2] = 0
                    else:
                        currentJob.jobsLabel.emit(4,
                                                  self.parent.jobsLabel[4] + 1)
                        lstTotal[0] += 100

                # End Processing

                currentJob.progressBar.emit(0, nTotal)

                currentStatus = self.jobs.status(currentJob.jobID)

                if currentStatus in [JobStatus.Abort, JobStatus.AbortJob]:
                    self.jobs.status(currentJob.jobID, JobStatus.Aborted)
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "Job {} - Aborted.\n\n\n".format(currentJob.jobID),
                        {'color': Qt.blue})
                else:
                    self.jobs.status(currentJob.jobID, JobStatus.Done)
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "Job {} - Done.\n\n\n".format(currentJob.jobID),
                        {'color': Qt.blue})

            else:

                self.jobs.status(currentJob.jobID, JobStatus.Error)

                msg = "FM0026: Error in construction of command - {}\n\n".format(
                    objCommand.error),

                currentJob.outputJobMain(currentJob.jobID,
                                         msg, {'color': Qt.red},
                                         error=True)

                if self.log:
                    MODULELOG.info("MCW0011: Error Base files in Process: %s",
                                   str(objCommand.baseFiles))
                    MODULELOG.info(
                        "MCW0012: Error Source files in Process: %s",
                        str(objCommand.sourceFiles))

        currentJob.jobsLabel.emit(1, currentJob.jobID)
        currentJob.jobsLabel.emit(2, 0)

        # No more jobs on queue
        self.jobs.jobsStatus(JobStatus.Done)

        return None


class CurrentJob:  # pylint: disable=R0903
    """Helper class for working with a job"""

    def __init__(self):

        self.jobID = None
        self.status = None
        self.command = None
        self.outputMain = None
        self.outputJobMain = None
        self.outputJobError = None
        self.progressBar = None
        self.controlQueue = None
        self.spControlQueue = None
        self.jobsLabel = None


class ValidateCommand(QValidator):
    """Validate command line entered"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

    def validate(self, inputStr, pos):
        """Check regex in VerifyMKVCommand"""

        verify = mkv.VerifyMKVCommand(inputStr)

        if verify:
            if self.parent.objCommand is None:
                self.parent.objCommand = mkv.MKVCommand(inputStr)
            else:
                self.parent.objCommand.command = inputStr

            self.parent.setOutputFileSignal.emit(self.parent.objCommand)

            self.parent.buttonsState(True)

            self.parent.btnReset.setEnabled(True)

            if self.parent.log:
                MODULELOG.debug("MCW0002: Command Ok: [%s]", inputStr)
        else:
            self.parent.buttonsState(False)
            self.parent.renameWidget.clear()
            self.parent.objCommand = None

            if self.parent.log:
                MODULELOG.debug("MCW0003: Command not Ok: [%s]", inputStr)

        return (QValidator.Acceptable, inputStr, pos)


class WorkerSignals(threads.WorkerSignals):
    """Additional signals for QRunables"""

    jobslabel = Signal(int, object)
    progress = Signal(int, int)
    outputmain = Signal(str, dict)
    outputcommand = Signal(str)


class Worker(threads.Worker):  # pylint: disable=R0903
    """QRunnable worker with additional callbacks"""

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__(fn, *args, **kwargs)

        # Override signals variable with extended one
        self.signals = WorkerSignals()

        # Add the callback to kwargs
        self.kwargs['cbProgress'] = self.signals.progress
        self.kwargs['cbOutputMain'] = self.signals.outputmain
        self.kwargs['cbOutputCommand'] = self.signals.outputcommand
        self.kwargs['cbJobsLabel'] = self.signals.jobslabel


def _outputError(currentJob, message):
    """output error to job main and error output widgets"""

    currentJob.outputJobMain(currentJob.jobID, message, {'color': Qt.red})
    currentJob.outputJobError(currentJob.jobID, message, {'color': Qt.red})
