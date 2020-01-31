"""
class CommandWidget
"""
import logging
import threading

from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QLineEdit,
)

from vsutillib.pyqt import OutputTextWidget, QPushButtonWidget
from vsutillib.process import isThreadRunning

from .. import config
from ..jobs import JobStatus
from ..utils import Text, ValidateCommand, yesNoDialog

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(QWidget):
    """Output for running queue"""

    # log state
    __log = False
    insertTextSignal = Signal(str, dict)
    updateCommandSignal = Signal(str)
    cmdValidationSignal = Signal(bool)

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

    def __init__(self, parent=None, proxyModel=None):
        super(CommandWidget, self).__init__(parent)

        self.parent = parent
        self.proxyModel = proxyModel
        self.tableModel = proxyModel.sourceModel()

        self.cmdValidationSignal.connect(self.cmdValidation)
        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.watchJobs)
        # self.timer.start()

        self._initControls()
        self._initUI()
        self._initHelper()

    def _initControls(self):

        self.outputWindow = OutputTextWidget(self)

        self.frmCmdLine = QFormLayout()
        btnAddCommand = QPushButtonWidget(
            Text.txt0160, function=lambda: self.addCommand(JobStatus.Waiting), toolTip=Text.txt0161
        )
        self.cmdLine = QLineEdit()
        #validator = ValidateCommand(self)
        self.cmdLine.setValidator(ValidateCommand(self, self.cmdValidationSignal))

        self.frmCmdLine.addRow(btnAddCommand, self.cmdLine)

        self.command = QWidget()
        self.command.setLayout(self.frmCmdLine)

        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        btnPasteClipboard = QPushButtonWidget(
            "Paste",
            function=self.pasteClipboard,
            toolTip="Paste Clipboard contents in command line",
        )

        btnAddQueue = QPushButtonWidget(
            "Add Queue",
            function=lambda: self.addCommand(JobStatus.AddToQueue),
            toolTip="Add command to jobs table and put on Queue",
        )

        btnClear = QPushButtonWidget(
            Text.txt0162, function=self.clearOutputWindow, toolTip=Text.txt0163
        )

        self.btnGrid.addWidget(btnPasteClipboard, 0, 0)
        self.btnGrid.addWidget(btnAddQueue, 1, 0)
        self.btnGrid.addWidget(btnClear, 2, 0)
        self.btnGroup.setLayout(self.btnGrid)

    def _initUI(self):

        grid = QGridLayout()

        grid.addWidget(self.command, 0, 0, 1, 2)
        grid.addWidget(self.btnGroup, 1, 0)
        grid.addWidget(self.outputWindow, 1, 1, 10, 1)

        self.setLayout(grid)

    def _initHelper(self):

        # map insertText signal to outputWidget one
        self.insertText = self.outputWindow.insertTextSignal


        # command
        self.cmdLine.setClearButtonEnabled(True)
        self.updateCommandSignal.connect(self.updateCommand)
        self.cmdValidationSignal.connect(self.cmdValidation)
        self.frmCmdLine.itemAt(0, QFormLayout.LabelRole).widget().setEnabled(False)

        # clear button
        self.btnGrid.itemAt(config.BTNADDQUEUE).widget().setEnabled(False)
        self.btnGrid.itemAt(config.BTNCLEAR).widget().setEnabled(False)
        self.outputWindow.textChanged.connect(self.clearButtonsState)

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

        return OutputTextWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def watchJobs(self):

        totalThreads = threading.activeCount()
        print(f'Running threads = {totalThreads}')

        bTest = isThreadRunning('jobsWorker')

        print(f'Jobs worker running {bTest}')


    def addCommand(self, status):

        totalJobs = self.tableModel.rowCount()
        command = self.cmdLine.text()
        data = [['', ''], [status, "Status code"], [command, command]]
        self.tableModel.insertRows(totalJobs, 1, data=data)

        self.cmdLine.clear()

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            self.updateCommand(clip)

    @Slot(bool)
    def cmdValidation(self, validateOK):

        addCommand = self.frmCmdLine.itemAt(0, QFormLayout.LabelRole).widget()
        addCommand.setEnabled(validateOK)

    @Slot(str)
    def updateCommand(self, command):
        """Update command input widget"""

        self.cmdLine.clear()
        self.cmdLine.setText(command)
        self.cmdLine.setCursorPosition(0)

    def clearButtonsState(self):
        """Set clear button state"""
        if self.outputWindow.toPlainText() != "":
            self.btnGrid.itemAt(config.BTNCLEAR).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(config.BTNCLEAR).widget().setEnabled(False)

    def buttonsState(self):
        """Set button state according to valid input on command line"""
        if self.outputWindow.toPlainText() != "":
            self.btnGrid.itemAt(config.BTNCLEAR).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(config.BTNCLEAR).widget().setEnabled(False)

    def clearOutputWindow(self):
        """
        clearOutputWindow clear the command output window
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False

        # Clear output window?
        title = _(Text.txt0083)
        msg = "¿" if language == "es" else ""
        msg += _("Text.txt0084") + "?"

        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.outputWindow.clear()

    def setLanguage(self):
        """
        setLanguage language use in buttons/labels to be called by MainWindow
        """

        for index in range(self.frmCmdLine.rowCount()):
            widget = self.frmCmdLine.itemAt(index, QFormLayout.LabelRole).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setStatusTip(_(widget.toolTip))

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setStatusTip(_(widget.toolTip))
