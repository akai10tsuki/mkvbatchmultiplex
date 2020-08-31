"""
class CommandWidget
"""

import logging
import time

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QColor, QPalette
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
    QOutputTextWidget,
    QPushButtonWidget,
    qtRunFunctionInThread,
    SvgColor,
)
from vsutillib.process import isThreadRunning
from vsutillib.pyqt import (
    checkColor,
    HorizontalLine,
    LineOutput,
    messageBox,
    TabWidgetExtension,
)

# from vsutillib.mkv import MKVCommand, MKVCommandParser
from vsutillib.mkv import MKVCommandParser

from .. import config
from ..jobs import JobStatus
from ..utils import Text, ValidateCommand, yesNoDialog

from .CommandWidgetsHelpers import checkFiles, runAnalysis, showCommands

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(TabWidgetExtension, QWidget):
    """Output for running queue"""

    # log state
    __log = False
    insertTextSignal = Signal(str, dict)
    updateCommandSignal = Signal(str)
    cliButtonsSateSignal = Signal(bool)
    cliValidateSignal = Signal(bool)
    resetSignal = Signal()

    def __init__(self, parent=None, proxyModel=None, controlQueue=None, log=None):
        super(CommandWidget, self).__init__(parent=parent, tabWidgetChild=self)

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
        self.outputWindow = QOutputTextWidget(self)
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
            Text.txt0164, function=self.pasteClipboard, toolTip=Text.txt0165,
        )
        self.cmdLine = QLineEdit()
        self.cmdLine.setValidator(
            ValidateCommand(self, self.cliValidateSignal, log=self.log)
        )
        self.frmCmdLine.addRow(btnPasteClipboard, self.cmdLine)
        self.frmCmdLine.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.command = QWidget()
        self.command.setLayout(self.frmCmdLine)

        #
        # Button group definition
        #
        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        btnAddCommand = QPushButtonWidget(
            Text.txt0160,
            function=lambda: self.addCommand(JobStatus.Waiting),
            toolTip=Text.txt0161,
        )
        btnRename = QPushButtonWidget(
            Text.txt0182,
            function=self.parent.renameWidget.setAsCurrentTab,
            toolTip=Text.txt0183,
        )
        btnAddQueue = QPushButtonWidget(
            Text.txt0166,
            function=lambda: self.addCommand(JobStatus.AddToQueue),
            toolTip=Text.txt0167,
        )
        btnStartQueue = QPushButtonWidget(
            Text.txt0126, function=self.parent.jobsQueue.run, toolTip=Text.txt0169,
        )
        btnAnalysis = QPushButtonWidget(
            Text.txt0170,
            function=lambda: qtRunFunctionInThread(
                runAnalysis,
                command=self.cmdLine.text(),
                output=self.output,
                log=self.log,
            ),
            toolTip=Text.txt0171,
        )
        btnShowCommands = QPushButtonWidget(
            Text.txt0172,
            function=lambda: qtRunFunctionInThread(
                showCommands,
                output=self.output,
                command=self.cmdLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            toolTip=Text.txt0173,
        )
        btnCheckFiles = QPushButtonWidget(
            Text.txt0174,
            function=lambda: qtRunFunctionInThread(
                checkFiles,
                output=self.output,
                command=self.cmdLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            toolTip=Text.txt0175,
        )
        btnClear = QPushButtonWidget(
            Text.txt0176, function=self.clearOutputWindow, toolTip=Text.txt0177,
        )
        btnReset = QPushButtonWidget(
            Text.txt0178, function=self.reset, toolTip=Text.txt0179,
        )

        self.btnGrid.addWidget(btnAddCommand, 0, 0)
        self.btnGrid.addWidget(btnRename, 0, 1)
        self.btnGrid.addWidget(btnAddQueue, 1, 0)
        self.btnGrid.addWidget(btnStartQueue, 1, 1)
        self.btnGrid.addWidget(HorizontalLine(), 2, 0, 1, 2)
        self.btnGrid.addWidget(btnAnalysis, 3, 0)
        self.btnGrid.addWidget(btnShowCommands, 3, 1)
        self.btnGrid.addWidget(btnCheckFiles, 4, 0)
        self.btnGrid.addWidget(HorizontalLine(), 5, 0, 1, 2)
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
        # self.frmCmdLine.itemAt(0, QFormLayout.LabelRole).widget().setEnabled(False)
        self.cliButtonsState(False)
        self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(False)

        # Clear buttons related
        self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.RESET).widget().setEnabled(False)

        # connect text windows textChanged to clearButtonState function
        self.outputWindow.textChanged.connect(self.clearButtonState)

        # connect command line textChanged to analysisButtonState function
        self.cmdLine.textChanged.connect(self.analysisButtonState)

        # Job Queue related
        self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)

        # Job Added to Queue
        self.parent.jobsQueue.addQueueItemSignal.connect(self.printJobIDAdded)

        #
        # Misc
        #
        self.cmdLine.setClearButtonEnabled(True)  # button at end of line to clear it

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
        """Update the command object"""

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
            color = checkColor(
                QColor(42, 130, 218), config.data.get(config.ConfigKey.DarkMode)
            )
            palette.setColor(QPalette.WindowText, color)
            self.parent.jobsLabel.setPalette(palette)
        else:
            palette = QPalette()
            color = checkColor(None, config.data.get(config.ConfigKey.DarkMode))
            palette.setColor(QPalette.WindowText, color)
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
        # [cell value, tooltip, obj]
        data = [
            ["", "", None],
            [status, "Status code", None],
            [command, command, self.oCommand],
        ]
        self.model.insertRows(totalJobs, 1, data=data)
        self.cmdLine.clear()

    def printJobIDAdded(self, index):

        jobID = self.model.dataset[index.row(), index.column()]

        self.output.command.emit(
            f"Job: {jobID} added to Queue...\n", {LineOutput.AppendEnd: True}
        )

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

    def analysisButtonState(self):
        """Set clear button state"""

        if self.cmdLine.text() != "":
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(False)

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
