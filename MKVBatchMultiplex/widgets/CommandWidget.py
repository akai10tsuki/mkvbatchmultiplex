"""
CommandWidget Class: Class to read the mkvtoolnix-gui command

"""
# Next Log ID: CMD0001

# region imports
import logging

from collections import deque
from typing import Optional

from PySide6.QtCore import QEvent, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
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
    QCheckBoxWidget,
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
    clearCommandSignal = Signal()

    # region initialization/

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            proxyModel: Optional[QWidget] = None,
            rename: Optional[QWidget] = None,
            controlQueue: Optional[deque] = None,
            log: Optional[bool] = None) -> None:
        super().__init__(parent=parent)

        # properties
        self.__log = None
        self.__output: OutputWindows = None
        self.__rename = rename

        self.parent = parent
        self.proxyModel = proxyModel
        self.controlQueue = controlQueue

        self._initVars()
        self._initControls()
        self._initHelper()
        self._initUI()
        self._installEventFilter()

        # log updates outputWindow.log
        self.log = log

    def _initVars(self) -> None:
        #
        #
        #
        useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)

        self.algorithm = None
        self.oCommand = MKVCommandParser(
            appDir=self.parent.appDirectory,
            useEmbedded=useEmbedded,
            log=self.log)
        self.model = self.proxyModel.sourceModel()

        #
        # command line
        #
        self.frmCommandLine = QFormLayout()
        self.commandLine = QLineEdit(objectName=_ObjectName.commandLine)
        # Increase command line buffer to 64k default is 32k
        self.commandLine.setMaxLength(65536)
        self.commandWidget = QWidget()

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

        self.crcGroupBox = QGroupBox()
        self.crcHBox = QHBoxLayout()

        self.chkBoxCRC = None

    def _initControls(self) -> None:

        # region command line
        btnPasteClipboard = QPushButtonWidget(
            Text.txt0164,
            function=lambda: qtRunFunctionInThread(self.pasteClipboard),
            margins="  ",
            toolTip=Text.txt0165,
            objectName=_ObjectName.btnPasteClipboard,
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
            objectName=_ObjectName.btnAddCommand,
        )
        #    function=self.parent.renameWidget.setAsCurrentTab,
        btnRename = QPushButtonWidget(
            Text.txt0182,
            function=self.rename.setAsCurrentTab,
            margins=" ",
            toolTip=Text.txt0183,
            objectName=_ObjectName.btnRename,
        )
        btnAddQueue = QPushButtonWidget(
            Text.txt0166,
            function=lambda: self.addCommand(JobStatus.AddToQueue),
            margins=" ",
            toolTip=Text.txt0167,
            objectName=_ObjectName.btnAddQueue
        )
        # function=self.parent.jobsQueue.run,
        btnStartWorker = QPushButtonWidget(
            Text.txt0126,
            function=self.startWorker,
            margins=" ",
            toolTip=Text.txt0169,
            objectName=_ObjectName.btnStartWorker,
        )
        # runAnalysis
        btnAnalysis = QPushButtonWidget(
            Text.txt0170,
            function=lambda: qtRunFunctionInThread(
                runAnalysis,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                output=self.output,
                appDir=self.parent.appDirectory,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0171,
            objectName=_ObjectName.btnAnalysis,
        )
        # showCommands
        btnShowCommands = QPushButtonWidget(
            Text.txt0172,
            function=lambda: qtRunFunctionInThread(
                showCommands,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                appDir=self.parent.appDirectory,
                log=self.log,

            ),
            margins=" ",
            toolTip=Text.txt0173,
            objectName=_ObjectName.btnShowCommands,
        )
        # checkFiles
        btnCheckFiles = QPushButtonWidget(
            Text.txt0174,
            function=lambda: qtRunFunctionInThread(
                checkFiles,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                appDir=self.parent.appDirectory,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0175,
            objectName=_ObjectName.btnCheckFiles,
        )
        # source tree
        btnFilesTree = QPushButtonWidget(
            Text.txt0184,
            function=lambda: qtRunFunctionInThread(
                sourceTree,
                output=self.output,
                command=self.commandLine.text(),
                oCommand=self.oCommand,
                appDir=self.parent.appDirectory,
                log=self.log,
            ),
            margins=" ",
            toolTip=Text.txt0175,
            objectName=_ObjectName.btnFilesTree,
        )
        btnClear = QPushButtonWidget(
            Text.txt0162,
            function=self.clearOutputWindow,
            margins=" ",
            toolTip=Text.txt0177,
            objectName=_ObjectName.btnClear
        )
        btnReset = QPushButtonWidget(
            Text.txt0178,
            function=self.reset,
            margins=" ",
            toolTip=Text.txt0179,
            objectName=_ObjectName.btnReset
        )

        self.btnGrid.addWidget(btnAddCommand, 0, 0)
        self.btnGrid.addWidget(btnRename, 0, 1)
        self.btnGrid.addWidget(btnAddQueue, 1, 0)
        self.btnGrid.addWidget(btnStartWorker, 1, 1)
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
        #self.algorithmGroupBox = QGroupBox()
        #self.algorithmHBox = QHBoxLayout()
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

        self.chkBoxCRC = QCheckBoxWidget(Text.txt0185, textPrefix=" ")
        self.crcHBox.addWidget(self.chkBoxCRC)
        self.crcGroupBox.setLayout(self.crcHBox)
        # endregion CRC32

    def _initHelper(self) -> None:

        # button at end of line to clear it
        self.commandLine.setClearButtonEnabled(True)
        self.commandLine.setObjectName(_ObjectName.commandLine)
        commandLine = self.getButton(_Button.COMMANDLINE)
        commandLine.setObjectName(_ObjectName.commandLine)
        commandLine.installEventFilter(self)

        pasteButton = self.getButton(_Button.PASTE)
        pasteButton.installEventFilter(self)

        #pasteButton.setDefault(True)
        #pasteButton.setFocus()
        #pasteButton.grabKeyboard()

        # command line related signals
        self.updateCommandSignal.connect(self.updateCommand)
        self.cliValidateSignal.connect(self.cliValidate)
        self.cliValidateSignal.connect(self.cliButtonsState)
        self.cliValidateSignal.connect(self.updateObjCommand)

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
        self.commandLine.textChanged.connect(self.rename.undoButtonState)

        # Job Queue related
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobStartWorkerState(True)
        )
        self.parent.jobsQueue.runJobs.startSignal.connect(
            lambda: self.jobStartWorkerState(False)
        )
        self.btnGrid.itemAt(_Button.STARTWORKER).widget().setEnabled(False)

    def _initUI(self) -> None:

        grid = QGridLayout()
        grid.addWidget(self.commandWidget, 0, 0, 1, 2)
        grid.addWidget(self.algorithmGroupBox, 1, 0)
        grid.addWidget(self.crcGroupBox, 1, 1)
        grid.addWidget(self.btnGroup, 2, 0)
        grid.addWidget(self.outputWindow, 2, 1, 10, 1)

        self.setLayout(grid)

    def _installEventFilter(self) -> None:

        for b in [
            _Button.PASTE,
            _Button.COMMANDLINE,
            _Button.ADDCOMMAND,
            _Button.RENAME,
            _Button.ADDQUEUE,
            _Button.STARTWORKER,
            _Button.ANALYSIS,
            _Button.SHOWCOMMANDS,
            _Button.CHECKFILES,
            _Button.FILESTREE,
            _Button.CLEAR,
            _Button.RESET,
        ]:
            button = self.getButton(b)
            button.installEventFilter(self)

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
        """Slot for setting logging through signal"""
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
    # endregion properties

    # region buttons

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
                if b == _Button.ADDQUEUE:
                    if validateOK:
                        #button.setFocus(Qt.FocusReason.OtherFocusReason)
                        #button.setDefault(True)
                        pass
                    else:
                        #button.setDefault(False)
                        pass

    # Slot for the update command signal
    @Slot(bool)
    def cliValidate(self, validateOK: bool) -> None:
        """
        cliValidate Slot used by ValidateCommand

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
        self.updateObjCommand(validateOK)

    @Slot(bool)
    def jobStartWorkerState(self, state):

        if state and not isThreadRunning(config.WORKERTHREADNAME):
            self.btnGrid.itemAt(_Button.STARTWORKER).widget().setEnabled(True)
            #self.btnGrid.itemAt(_Button.STARTWORKER).widget().setDefault(True)
        else:
            self.btnGrid.itemAt(_Button.STARTWORKER).widget().setEnabled(False)
            #self.btnGrid.itemAt(_Button.STARTWORKER).widget().setDefault(False)

    @Slot()
    def setDefaultAlgorithm(self) -> None:
        if config.data.get(config.ConfigKey.Algorithm) is not None:
            currentAlgorithm = config.data.get(config.ConfigKey.Algorithm)
            self.radioButtons[currentAlgorithm].setChecked(True)

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

    @Slot()
    def translate(self) -> None:
        """
        Set language used in buttons/labels called in MainWindow
        """

        for index in range(self.frmCommandLine.rowCount()):
            widget = self.frmCommandLine.itemAt(
                index, QFormLayout.LabelRole).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.translate()

        widgetGroups = [self.btnGrid, self.algorithmHBox, self.crcHBox]
        for gWidget in widgetGroups:
            for index in range(gWidget.count()):
                widget = gWidget.itemAt(index).widget()
                if isinstance(
                    widget,
                    (
                        QCheckBoxWidget,
                        QLabelWidget,
                        QPushButtonWidget,
                    ),
                ):
                    widget.translate()

        #for index in range(self.btnGrid.count()):
        #    widget = self.btnGrid.itemAt(index).widget()
        #    if isinstance(widget, QPushButtonWidget):
        #        widget.translate()

        #for index in range(self.algorithmHBox.count()):
        #    widget = self.algorithmHBox.itemAt(index).widget()
        #    if isinstance(
        #        widget,
        #        (
        #            QLabelWidget,
        #            QPushButtonWidget,
        #        ),
        #    ):
        #        widget.translate()

        #for index in range(self.crcHBox.count()):
        #    widget = self.crcHBox.itemAt(index).widget()
        #    if isinstance(
        #        widget,
        #        (
        #            QCheckBoxWidget,
        #            QLabelWidget,
        #            QPushButtonWidget,
        #        ),
        #    ):
        #        widget.translate()

    @Slot(bool)
    def updateObjCommand(self, valid):
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

    @Slot(list)
    def applyRename(self, renameFiles):
        """
        Works with applyFileRenameSignal generated by renameWidget
        """

        if self.oCommand:
            self.oCommand.renameOutputFiles(renameFiles)
    # endregion button slots

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
        self.jobStartWorkerState(False)
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

    def toggledRadioButton(self) -> None:
        for index, rb in enumerate(self.radioButtons):
            if rb.isChecked():
                self.algorithm = index

    def crcCheckBoxStateChanged(self, state) -> None:
        # Instead of a Qt.CheckState value state is a number
        if config.data.get(config.ConfigKey.CRC32) is not None:
            config.data.set(config.ConfigKey.CRC32, state)

    def analysisButtonState(self) -> None:
        """Set clear button state"""

        if self.commandLine.text() != "":
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(True)
            self.clearCommandSignal.emit()
        else:
            self.btnGrid.itemAt(_Button.ANALYSIS).widget().setEnabled(False)

    def clearButtonState(self) -> None:
        """Set clear button state"""

        if self.outputWindow.toPlainText() != "":
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.CLEAR).widget().setEnabled(False)

    # endregion buttons

    # region events
    def eventFilter(self, source, event):
        """Work with the setDefault of Buttons"""

        objectName = source.objectName()

        if event.type() == QEvent.FocusIn:
            print('filter-focus-in:', objectName)
            if objectName == _ObjectName.commandLine:
                button = self.getButton(_Button.PASTE)
                #button.releaseKeyboard()
                #button.setDefault(False)
            elif objectName == _ObjectName.btnPasteClipboard:
                button = self.getButton(_Button.PASTE)
                #button.setDefault(True)
        elif event.type() == QEvent.FocusOut:
            print('filter-focus-out:', objectName)
            if objectName == _ObjectName.btnPasteClipboard:
                button = self.getButton(_Button.PASTE)
                #button.setDefault(False)

        return super().eventFilter(source, event)
    # end region events

    def getButton(self, whichWidget) -> QWidget:

        if whichWidget in [_Button.PASTE, _Button.COMMANDLINE]:
            if widget := self.frmCommandLine.itemAt(whichWidget).widget():
                return widget
        else:
            if button := self.btnGrid.itemAt(whichWidget).widget():
                return button

        return None


class _Button:
    """
    Index of the buttons (Yes COMMANDLINE is not a button)
    """

    DEFAULTALGORITHM = 5

    PASTE = 0
    COMMANDLINE = 1

    ADDCOMMAND = 0
    RENAME = 1
    ADDQUEUE = 2
    STARTWORKER = 3

    ANALYSIS = 5
    SHOWCOMMANDS = 6
    CHECKFILES = 7
    FILESTREE = 8

    CLEAR = 10
    RESET = 11

class _ObjectName:

    btnPasteClipboard = "btnPasteClipboard"
    commandLine = "commandLine"
    btnDefaultAlgorithm = "btnDefaultAlgorithm"
    btnAddCommand = "btnAddCommand"
    btnRename = "btnRename"
    btnAddQueue = "btnAddQueue"
    btnStartWorker = "btnStartWorker"
    btnAnalysis = "btnAnalysis"
    btnShowCommands = "btnShowCommands"
    btnCheckFiles = "btnCheckFiles"
    btnFilesTree = "btnFilesTree"
    btnClear = "btnClear"
    btnReset = "btnReset"


# This if for Pylance _() is not defined
def _(dummy):
    return dummy


del _
