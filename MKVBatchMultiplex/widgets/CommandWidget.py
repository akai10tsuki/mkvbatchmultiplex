"""
CommandWidget Class: Class to read the mkvtoolnix-gui command

"""
# Next Log ID: CMD0001

# region imports
import logging
from collections import deque
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QWidget
)

from vsutillib.mkv import MKVCommandParser
from vsutillib.process import isThreadRunning
from vsutillib.pyside6 import (
    HorizontalLine,
    LineOutput,
    QLabelWidget,
    QOutputTextWidget,
    QPushButtonWidget,
    messageBox,
    qtRunFunctionInThread
)

from .. import config
from ..jobs import JobStatus
from ..utils import OutputWindows, Text, ValidateCommand, yesNoDialog
from .CommandWidgetsHelpers import (
    checkFiles,
    runAnalysis,
    showCommands,
    sourceTree
)
# endregion imports

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(QWidget):
    """
    Receives and analyze the command from mkvtoolnix-gui
    """

    # logging state
    __log = False

    # signals
    insertTextSignal = Signal(str, dict)
    updateCommandSignal = Signal(str)
    resetCommandSignal = Signal()
    cliValidateSignal = Signal(bool)

    # region initialization

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            proxyModel: Optional[QWidget] = None,
            controlQueue: Optional[deque] = None,
            log: Optional[bool] = None) -> None:
        super().__init__(parent=parent)

        # properties
        self.__log = None
        self.__output: OutputWindows = None
        self.__rename = None

        self.parent = parent
        self.proxyModel = proxyModel
        self.controlQueue = controlQueue

        self._initVars()
        self._initControls()
        self._initHelper()
        self._initUI()

        # log updates outputWindow.log
        self.log = log

    def _initVars(self) -> None:
        #
        #
        #
        self.algorithm = None
        self.oCommand = MKVCommandParser()
        self.model = self.proxyModel.sourceModel()

        #
        # command line
        #
        self.frmCommandLine = QFormLayout()
        self.commandLine = QLineEdit()
        # Increase command line buffer to 64k default is 32k
        self.commandLine.setMaxLength(65536)
        self.commandWidget = QWidget()
        print(f"Line max length={self.commandLine.maxLength()}\n")

        self.outputWindow = QOutputTextWidget()

        #
        # Buttons
        #
        self.btnGroup = QGroupBox()
        self.btnGrid = QGridLayout()

        self.algorithmGroupBox = QGroupBox()
        self.algorithmHBox = QHBoxLayout()

        self.lblAlgorithm = None
        self.radioButtons = None
        self.rbZero = None
        self.rbOne = None
        self.rbTwo = None

    def _initControls(self) -> None:

        # region command line
        btnPasteClipboard = QPushButtonWidget(
            Text.txt0164,
            function=lambda: qtRunFunctionInThread(self.pasteClipboard),
            margins="  ",
            toolTip=Text.txt0165,
        )
        self.frmCommandLine.addRow(btnPasteClipboard, self.commandLine)
        self.frmCommandLine.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow)

        self.commandLine.setValidator(
            ValidateCommand(self, self.cliValidateSignal, log=self.log)
        )

        self.commandWidget.setLayout(self.frmCommandLine)
        # endregion command line

        # region Buttons
        btnAddCommand = QPushButtonWidget(
            Text.txt0160,
            function=lambda: self.addCommand(JobStatus.Waiting),
            margins=" ",
            toolTip=Text.txt0161,
        )

        #    function=self.parent.renameWidget.setAsCurrentTab,
        btnRename = QPushButtonWidget(
            Text.txt0182,
            function=self.parent.renameWidget.setAsCurrentTab,
            margins=" ",
            toolTip=Text.txt0183,
        )
        btnAddQueue = QPushButtonWidget(
            Text.txt0166,
            function=lambda: self.addCommand(JobStatus.AddToQueue),
            margins=" ",
            toolTip=Text.txt0167,
        )
        # function=self.parent.jobsQueue.run,
        btnStartQueue = QPushButtonWidget(
            Text.txt0126,
            function=self.startWorker,
            margins=" ",
            toolTip=Text.txt0169,
        )
        # runAnalysis
        btnAnalysis = QPushButtonWidget(
            Text.txt0170,
            function=lambda: qtRunFunctionInThread(
                runAnalysis,
                command=self.commandLine.text(),
                output=self.output,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0171,
        )
        # showCommands
        btnShowCommands = QPushButtonWidget(
            Text.txt0172,
            function=lambda: qtRunFunctionInThread(
                showCommands,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0173,
        )
        # checkFiles
        btnCheckFiles = QPushButtonWidget(
            Text.txt0174,
            function=lambda: qtRunFunctionInThread(
                checkFiles,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0175,
        )
        # source tree
        btnFilesTree = QPushButtonWidget(
            Text.txt0184,
            function=lambda: qtRunFunctionInThread(
                sourceTree,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0175,
        )

        btnClear = QPushButtonWidget(
            Text.txt0162,
            function=self.clearOutputWindow,
            margins=" ",
            toolTip=Text.txt0177,
        )
        btnReset = QPushButtonWidget(
            Text.txt0178,
            function=self.reset,
            margins=" ",
            toolTip=Text.txt0179,
        )

        self.btnGrid.addWidget(btnAddCommand, 0, 0)
        self.btnGrid.addWidget(btnRename, 0, 1)
        self.btnGrid.addWidget(btnAddQueue, 1, 0)
        self.btnGrid.addWidget(btnStartQueue, 1, 1)
        self.btnGrid.addWidget(HorizontalLine(), 2, 0, 1, 2)
        self.btnGrid.addWidget(btnAnalysis, 3, 0)
        self.btnGrid.addWidget(btnShowCommands, 3, 1)
        self.btnGrid.addWidget(btnCheckFiles, 4, 0)
        self.btnGrid.addWidget(btnFilesTree, 4, 1)
        self.btnGrid.addWidget(HorizontalLine(), 5, 0, 1, 2)
        self.btnGrid.addWidget(btnClear, 6, 0)
        self.btnGrid.addWidget(btnReset, 6, 1)
        self.btnGroup.setLayout(self.btnGrid)
        # endregion buttons

        # region Algorithm group
        self.algorithmGroupBox = QGroupBox()
        self.algorithmHBox = QHBoxLayout()
        self.lblAlgorithm = QLabelWidget(
            Text.txt0094,
            textSuffix=":  ",
        )
        self.rbZero = QRadioButton("0", self)
        self.rbOne = QRadioButton("1", self)
        self.rbTwo = QRadioButton("2", self)
        self.radioButtons = [self.rbZero, self.rbOne, self.rbTwo]

        btnDefaultAlgorithm = QPushButtonWidget(
            Text.txt0092,
            function=self.setDefaultAlgorithm,
            margins=" ",
            toolTip=Text.txt0093,
        )

        self.algorithmHBox.addWidget(self.lblAlgorithm)
        self.algorithmHBox.addWidget(self.rbZero)
        self.algorithmHBox.addWidget(self.rbOne)
        self.algorithmHBox.addWidget(self.rbTwo)
        self.algorithmHBox.addWidget(btnDefaultAlgorithm)
        self.algorithmGroupBox.setLayout(self.algorithmHBox)
        # endregion Algorithm group

        # region CRC32
        self.crcGroupBox = QGroupBox()
        self.crcHBox = QHBoxLayout()

        self.chkBoxCRC = QCheckBox(" " + Text.txt0185, self)
        self.crcHBox.addWidget(self.chkBoxCRC)
        self.crcGroupBox.setLayout(self.crcHBox)
        # endregion CRC32

    def _initHelper(self) -> None:

        # button at end of line to clear it
        self.commandLine.setClearButtonEnabled(True)
        # command line related signals
        self.updateCommandSignal.connect(self.updateCommand)
        self.cliValidateSignal.connect(self.cliValidate)
        self.cliValidateSignal.connect(self.cliButtonsState)
        self.cliValidateSignal.connect(self.updateObjCommnad)

        # Algorithm radio buttons
        self.rbZero.toggled.connect(lambda: self.toggledRadioButton)
        self.rbOne.toggled.connect(lambda: self.toggledRadioButton)
        self.rbTwo.toggled.connect(lambda: self.toggledRadioButton)

        self.setDefaultAlgorithm()

        # CRC check box
        self.chkBoxCRC.stateChanged.connect(self.crcCheckBoxStateChanged)

        self.setDefaultCRC()

        # Buttons state
        self.cliButtonsState(False)
        self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(False)

        # Clear buttons related
        self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.RESET).widget().setEnabled(False)

        # connect text windows textChanged to clearButtonState function
        self.outputWindow.textChanged.connect(self.clearButtonState)

        # connect command line textChanged to analysisButtonState function
        self.commandLine.textChanged.connect(self.analysisButtonState)

        # Job Queue related
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobStartQueueState(True)
        )
        self.parent.jobsQueue.runJobs.startSignal.connect(
            lambda: self.jobStartQueueState(False)
        )
        self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)

    def _initUI(self) -> None:

        grid = QGridLayout()
        grid.addWidget(self.commandWidget, 0, 0, 1, 2)
        grid.addWidget(self.algorithmGroupBox, 1, 0)
        grid.addWidget(self.crcGroupBox, 1, 1)
        grid.addWidget(self.btnGroup, 2, 0)
        grid.addWidget(self.outputWindow, 2, 1, 10, 1)

        self.setLayout(grid)

    # endregion Initialization

    # region Logging setup

    @classmethod
    def classLog(cls, setLogging: Optional[bool] = None) -> bool:
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
    def log(self) -> bool:
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
    def log(self, value: bool) -> None:
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value
            self.outputWindow.log = value

    @Slot(bool)
    def setLog(self, bLogging: bool) -> None:
        """Slot for setting loggin through signal"""
        self.log = bLogging

    # endregion Logging setup

    # region properties

    @property
    def rename(self):
        return self.__rename

    @rename.setter
    def rename(self, value) -> None:
        if isinstance(value, object):
            self.__rename = value

    @property
    def output(self) -> OutputWindows:
        return self.__output

    @output.setter
    def output(self, value: OutputWindows) -> None:
        self.__output = value

    # endregion

    # region buttons slots
    @Slot(bool)
    def cliButtonsState(self, validateOK: bool) -> None:
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
            _Button.FILESTREE,
        ]:
            if button := self.btnGrid.itemAt(b).widget():
                button.setEnabled(validateOK)

    # Slot for the update commnad signal
    @Slot(bool)
    def cliValidate(self, validateOK: bool) -> None:
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
            if self.commandLine.text() != "":
                self.output.command.emit(
                    "Bad command.\n", {LineOutput.AppendEnd: True})

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
            self.oCommand.command = self.commandLine.text()
            if self.rename is not None:
                self.rename.setFilesSignal.emit(self.oCommand)
                self.rename.applyFileRenameSignal.connect(self.applyRename)
        else:
            self.oCommand.command = ""
            if self.rename is not None:
                self.rename.clear()

    @Slot(str)
    def updateCommand(self, command: str) -> None:
        """
        Update command input widget
        """

        self.commandLine.clear()
        self.commandLine.setText(command)
        self.commandLine.setCursorPosition(0)

    @Slot()
    def translate(self) -> None:
        """
        Set language used in buttons/lables called in MainWindow
        """

        for index in range(self.frmCommandLine.rowCount()):
            widget = self.frmCommandLine.itemAt(
                index, QFormLayout.LabelRole).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.translate()
    # endregion buttons slots

    # region buttons

    def pasteClipboard(self) -> None:
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            # self.output.command.emit(
            #    "Checking command...\n", {LineOutput.AppendEnd: True}
            # )
            self.update()
            self.updateCommandSignal.emit(clip)

    def addCommand(self, status: str) -> None:
        """
        addCommand add command row in jobs table

        Args:
            status (JobStatus): Status for job to be added should be either
                                JobStatus.Waiting or JobStatus.AddToQueue
        """

        totalJobs = self.model.rowCount()
        command = self.commandLine.text()
        data = [
            ["", "", self.algorithm],
            [status, "Status code", None],
            [command, command, self.oCommand],
        ]
        self.model.insertRows(totalJobs, 1, data=data)
        self.commandLine.clear()

    def startWorker(self) -> None:
        self.jobStartQueueState(False)
        self.parent.jobsQueue.run()

    def clearOutputWindow(self) -> None:
        """
        clearOutputWindow clear the command output window
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False

        # Clear output window
        title = _(Text.txt0180)
        msg = "¿" if language == "es" else ""
        msg += _(Text.txt0181) + "?"
        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.outputWindow.clear()

    def reset(self) -> None:
        """
        reset program status
        """

        language = config.data.get(config.ConfigKey.Language)

        if not isThreadRunning(config.WORKERTHREADNAME):

            language = config.data.get(config.ConfigKey.Language)
            bAnswer = False

            # Clear output window?
            title = _(Text.txt0178)
            msg = "¿" if language == "es" else ""
            msg += f"{_(Text.txt00176)}?"
            bAnswer = yesNoDialog(self, msg, title)

            if bAnswer:
                self.commandLine.clear()
                self.outputWindow.clear()
                self.output.jobOutput.clear()
                self.output.errorOutput.clear()
                self.resetCommandSignal.emit()

        else:
            messageBox(self, _(Text.txt0178), f"{_(Text.txt0089)}..")

    @Slot()
    def setDefaultAlgorithm(self) -> None:
        if config.data.get(config.ConfigKey.Algorithm) is not None:
            currentAlgorithm = config.data.get(config.ConfigKey.Algorithm)
            self.radioButtons[currentAlgorithm].setChecked(True)

    def toggledRadioButton(self) -> None:
        for index, rb in enumerate(self.radioButtons):
            if rb.isChecked():
                self.algorithm = index

    @Slot()
    def setDefaultCRC(self) -> None:
        if config.data.get(config.ConfigKey.CRC32) is not None:
            doCRC = config.data.get(config.ConfigKey.CRC32)
            if (doCRC == 2):
                self.chkBoxCRC.setCheckState(Qt.CheckState.Checked)
            elif (doCRC == 1):
                self.chkBoxCRC.setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                self.chkBoxCRC.setCheckState(Qt.CheckState.Unchecked)

    def crcCheckBoxStateChanged(self, state) -> None:
        # Instead of a Qt.CheckState value state is a number
        if config.data.get(config.ConfigKey.CRC32) is not None:
            config.data.set(config.ConfigKey.CRC32, state)

    def analysisButtonState(self) -> None:
        """Set clear button state"""

        if self.commandLine.text() != "":
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(False)

    def clearButtonState(self) -> None:
        """Set clear button state"""

        if self.outputWindow.toPlainText() != "":
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)

    # endregion buttons


class _Button:
    """
    Index of the buttons in btnGrid to enable/disable them
    """

    PASTE = 0

    ADDCOMMAND = 0
    RENAME = 1
    ADDQUEUE = 2
    STARTQUEUE = 3

    ANALYSIS = 5
    SHOWCOMMANDS = 6
    CHECKFILES = 7
    FILESTREE = 8

    CLEAR = 10
    RESET = 11


# This if for Pylance _() is not defined
def _(dummy):
    return dummy


del _
