"""
class CommandWidget
"""

# pylint: disable=bad-continuation

import logging
import time

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QFrame,
    QLineEdit,
    QMessageBox,
)

from vsutillib.pyqt import (
    OutputTextWidget,
    QPushButtonWidget,
    runFunctionInThread,
)
from vsutillib.process import isThreadRunning
from vsutillib.pyqt import messageBox, LineOutput
from vsutillib.mkv import MKVCommand, MKVCommandParser

from .. import config
from ..jobs import JobStatus
from ..utils import Text, ValidateCommand, yesNoDialog

from .CommandWidgetsHelpers import checkFiles, runAnalysis, showCommands

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(QWidget):
    """Output for running queue"""

    # log state
    __log = False
    insertTextSignal = Signal(str, dict)
    updateCommandSignal = Signal(str)
    cliButtonsSateSignal = Signal(bool)
    cliValidateSignal = Signal(bool)
    resetSignal = Signal()

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(self, parent=None, proxyModel=None, controlQueue=None, log=None):
        super(CommandWidget, self).__init__(parent)

        self.__log = log
        self.__output = None
        self.__rename = None
        self.__tab = None

        # self.oCommand = MKVCommand()
        self.oCommand = MKVCommandParser()
        self.controlQueue = controlQueue
        self.parent = parent
        self.proxyModel = proxyModel
        self.model = proxyModel.sourceModel()
        self.outputWindow = OutputTextWidget(self)
        self.log = log

        self._initControls()
        self._initUI()
        self._initHelper()

    def _initControls(self):
        #
        # command line
        #
        self.frmCmdLine = QFormLayout()
        btnPasteClipboard = QPushButtonWidget(
            "Paste",
            function=self.pasteClipboard,
            toolTip="Paste Clipboard contents in command line",
        )
        self.cmdLine = QLineEdit()
        self.cmdLine.setValidator(
            ValidateCommand(self, self.cliValidateSignal, log=self.log)
        )
        self.frmCmdLine.addRow(btnPasteClipboard, self.cmdLine)
        self.command = QWidget()
        self.command.setLayout(self.frmCmdLine)

        #
        # Button group definition
        #
        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Raised)
        line.setLineWidth(1)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Raised)
        line1.setLineWidth(1)

        btnAddCommand = QPushButtonWidget(
            Text.txt0160,
            function=lambda: self.addCommand(JobStatus.Waiting),
            toolTip=Text.txt0161,
        )
        btnRename = QPushButtonWidget(
            "Rename",
            function=self.parent.renameWidget.setCurrentIndexSignal.emit,
            toolTip="Rename output files",
        )
        btnAddQueue = QPushButtonWidget(
            "Add Queue",
            function=lambda: self.addCommand(JobStatus.AddToQueue),
            toolTip="Add command to jobs table and put on Queue",
        )
        btnStartQueue = QPushButtonWidget(
            "Start Queue",
            function=self.parent.jobsQueue.run,
            toolTip="Start processing jobs on Queue",
        )
        btnAnalysis = QPushButtonWidget(
            "Analysis",
            function=lambda: runFunctionInThread(
                runAnalysis,
                command=self.cmdLine.text(),
                output=self.output,
                log=self.log,
            ),
            toolTip="Print analysis of command line",
        )
        btnShowCommands = QPushButtonWidget(
            "Commands",
            function=lambda: runFunctionInThread(
                showCommands,
                output=self.output,
                command=self.cmdLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            toolTip="Commands to be applied",
        )
        btnCheckFiles = QPushButtonWidget(
            "Check Files",
            function=lambda: runFunctionInThread(
                checkFiles,
                output=self.output,
                command=self.cmdLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            toolTip="Check files for consistency",
        )
        btnClear = QPushButtonWidget(
            "Clear Output",
            function=self.clearOutputWindow,
            toolTip="Erase text in output window",
        )
        btnReset = QPushButtonWidget(
            "Reset",
            function=self.reset,
            toolTip="Reset state completely to work with another batch",
        )

        self.btnGrid.addWidget(btnAddCommand, 0, 0)
        self.btnGrid.addWidget(btnRename, 0, 1)
        self.btnGrid.addWidget(btnAddQueue, 1, 0)
        self.btnGrid.addWidget(btnStartQueue, 1, 1)
        self.btnGrid.addWidget(line, 2, 0, 1, 2)
        self.btnGrid.addWidget(btnAnalysis, 3, 0)
        self.btnGrid.addWidget(btnShowCommands, 3, 1)
        self.btnGrid.addWidget(btnCheckFiles, 4, 0)
        self.btnGrid.addWidget(line1, 5, 0, 1, 2)
        self.btnGrid.addWidget(btnClear, 6, 0)
        self.btnGrid.addWidget(btnReset, 6, 1)
        self.btnGroup.setLayout(self.btnGrid)

    def _initUI(self):

        grid = QGridLayout()
        grid.addWidget(self.command, 0, 0, 1, 2)
        grid.addWidget(self.btnGroup, 1, 0)
        grid.addWidget(self.outputWindow, 1, 1, 10, 1)

        self.setLayout(grid)

    def _initHelper(self):
        #
        # Signal interconnections
        #

        # local button state connect to related state
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobStartQueueState(True)
        )
        self.parent.jobsQueue.queueEmptiedSignal.connect(
            lambda: self.jobStartQueueState(False)
        )

        # job related
        self.parent.jobsQueue.runJobs.startSignal.connect(lambda: self.jobStatus(True))
        self.parent.jobsQueue.runJobs.finishedSignal.connect(
            lambda: self.jobStatus(False)
        )

        # map insertText signal to outputWidget one
        self.insertText = self.outputWindow.insertTextSignal

        # command
        self.updateCommandSignal.connect(self.updateCommand)
        self.cliButtonsSateSignal.connect(self.cliButtonsState)
        self.cliValidateSignal.connect(self.cliValidate)

        #
        # button state
        #

        # Command related
        #self.frmCmdLine.itemAt(0, QFormLayout.LabelRole).widget().setEnabled(False)
        self.cliButtonsState(False)

        # Clear buttons related
        self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.RESET).widget().setEnabled(False)

        # connect text windows textChanged to clearButtonState function
        self.outputWindow.textChanged.connect(self.clearButtonState)

        # Job Queue related
        self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)

        #
        # Misc
        #
        self.cmdLine.setClearButtonEnabled(True)  # button at end of line to clear it

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return CommandWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""

        if isinstance(value, bool) or value is None:
            self.__log = value
            # No variable used so for now use class log
            ValidateCommand.classLog(value)
            self.outputWindow.log = value

    @property
    def tab(self):
        return self.__tab

    @tab.setter
    def tab(self, value):
        self.__tab = value

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

    @property
    def rename(self):
        return self.__rename

    @rename.setter
    def rename(self, value):
        if isinstance(value, object):
            self.__rename = value

    @Slot(list)
    def applyRename(self, renameFiles):

        if self.oCommand:
            self.oCommand.renameOutputFiles(renameFiles)

    @Slot(bool)
    def cliButtonsState(self, validateOK):
        """
        cliButtonsState change enabled status for buttons related with command line

        Args:
            validateOK (bool): True to enable, False to disable
        """

        for b in [
            _Button.ADDCOMMAND,
            _Button.RENAME,
            _Button.ADDQUEUE,
            _Button.ANALYSIS,
            _Button.SHOWCOMMANDS,
            _Button.CHECKFILES,
        ]:
            button = self.btnGrid.itemAt(b).widget()
            button.setEnabled(validateOK)

    @Slot(bool)
    def cliValidate(self, validateOK):
        """
        cliValidate Slot used by ValidateCommnad

        Args:
            validateOK (bool): True if command line is Ok.  False otherwise.
        """

        if validateOK:
            self.output.command.emit(
                "Command looks ok.\n", {LineOutput.AppendEnd: True}
            )
        else:
            if self.cmdLine.text() != "":
                self.output.command.emit("Bad command.\n", {LineOutput.AppendEnd: True})

        self.cliButtonsState(validateOK)
        self.updateObjCommnad(validateOK)

    @Slot(bool)
    def jobStartQueueState(self, state):

        if state and not isThreadRunning(config.WORKERTHREADNAME):
            self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)

    @Slot(bool)
    def updateObjCommnad(self, valid):

        if valid:
            self.oCommand.command = self.cmdLine.text()
            if self.rename is not None:
                # Have to wait for MKVCommandParser finish reading files
                # while isThreadRunning("MKVPARSING"):
                #    time.sleep(0.5)
                self.rename.setFilesSignal.emit(self.oCommand)
                self.rename.applyFileRenameSignal.connect(self.applyRename)
        else:
            self.oCommand.command = ""
            if self.rename is not None:
                self.rename.clear()

    @Slot(str)
    def updateCommand(self, command):
        """Update command input widget"""

        self.cmdLine.clear()
        self.cmdLine.setText(command)
        self.cmdLine.setCursorPosition(0)

    @Slot(bool)
    def jobStatus(self, running):
        """
        jobStatus receive Signals for job start/end

        Args:
            running (bool): True if job started. False if ended.
        """

        if running:
            self.jobStartQueueState(False)
            palette = QPalette()
            palette.setColor(QPalette.WindowText, Qt.cyan)
            self.parent.jobsLabel.setPalette(palette)
        else:
            palette = QPalette()
            palette.setColor(QPalette.WindowText, Qt.white)
            self.parent.jobsLabel.setPalette(palette)

    def addCommand(self, status):
        """
        addCommand add command row in jobs table

        Args:
            status (JobStatus): Status for job to be added should be either
                                JobStatus.Waiting or JobStatus.AddToQueue
        """

        totalJobs = self.model.rowCount()
        command = self.cmdLine.text()
        data = [
            ["", "", None],
            [status, "Status code", None],
            [command, command, self.oCommand],
        ]
        self.model.insertRows(totalJobs, 1, data=data)
        self.cmdLine.clear()

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            self.output.command.emit(
                "Checking command...\n", {LineOutput.AppendEnd: True}
            )
            self.update()
            self.updateCommandSignal.emit(clip)

    def clearButtonState(self):
        """Set clear button state"""

        if self.outputWindow.toPlainText() != "":
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)

    def clearOutputWindow(self):
        """
        clearOutputWindow clear the command output window
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False

        # Clear output window?
        title = "Clear output"
        msg = "¿" if language == "es" else ""
        msg += "Clear output window" + "?"
        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.outputWindow.clear()

    def resetButtonState(self):
        """Set clear button state"""

        if self.output.jobOutput.toPlainText() != "":
            self.btnGrid.itemAt(_Button.RESET).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.RESET).widget().setEnabled(False)

    def reset(self):
        """
        reset program status
        """

        language = config.data.get(config.ConfigKey.Language)

        if not isThreadRunning(config.WORKERTHREADNAME):

            language = config.data.get(config.ConfigKey.Language)
            bAnswer = False

            # Clear output window?
            title = "Reset"
            msg = "¿" if language == "es" else ""
            msg += "Reset Application" + "?"
            bAnswer = yesNoDialog(self, msg, title)

            if bAnswer:
                self.cmdLine.clear()
                self.outputWindow.clear()
                self.output.jobOutput.clear()
                self.output.errorOutput.clear()
                self.resetSignal.emit()

        else:
            messageBox(self, "Reset", "Jobs are running..")

    def setLanguage(self):
        """
        setLanguage language use in buttons/labels to be called by MainWindow
        """

        for index in range(self.frmCmdLine.rowCount()):
            widget = self.frmCmdLine.itemAt(index, QFormLayout.LabelRole).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setToolTip(_(widget.toolTip))

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setToolTip(_(widget.toolTip))


class _Button:

    PASTE = 0

    ADDCOMMAND = 0
    RENAME = 1
    ADDQUEUE = 2
    STARTQUEUE = 3

    ANALYSIS = 5
    SHOWCOMMANDS = 6
    CHECKFILES = 7

    CLEAR = 9
    RESET = 10
