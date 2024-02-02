"""
RenameWidget:

This widget permit the rename of the output files in the MKVCommand

Also if files are drop from directories in the OS it will rename them.
"""

# LOG FW0013

import logging
import re
import sys

from pathlib import Path

from PySide6.QtCore import Signal, Qt, Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QGroupBox,
)

from vsutillib.pyside6 import (
    HorizontalLine,
    LineOutput,
    QLabelWidget,
    QOutputTextWidget,
    QPushButtonWidget,
    TabWidgetExtension,
    messageBox,
    qtRunFunctionInThread
)

from vsutillib.process import ThreadWorker
from vsutillib.files import crc32

from .. import config
from ..utils import computeCRC32, Text

from .RenameWidgetHelpers import (
    findDuplicates,
    RegExFilesWidget,
    RegExInputWidget,
    RegExLineInputWidget,
    resolveIncrements,
)

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class RenameWidget(TabWidgetExtension, QWidget):
    """Central widget"""

    # pylint: disable=too-many-instance-attributes
    # Defining elements of a GUI

    # Class logging state
    __log = False

    outputRenameResultsSignal = Signal(str, dict)
    outputOriginalFilesSignal = Signal(str, dict)
    applyFileRenameSignal = Signal(list)
    setFilesSignal = Signal(object)
    setCurrentIndexSignal = Signal()
    appendCRCSignal = Signal(int, Path)

    reCrcChars = re.compile('^[0123456789ABCDEF]+$', flags=re.IGNORECASE)

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

    def __init__(self, parent, controlQueue=None, log=None):
        super(RenameWidget, self).__init__(parent=parent, tabWidgetChild=self)

        self.__log = None
        self.__output = None
        self.parent = parent
        self.controlQueue = controlQueue
        self._initVars()
        self._initHelper()
        self._initUI()
        self.log = log

    def _initVars(self):

        #
        # Control variables
        #
        self._originalFileNames = []
        self._renameFileNames = []
        self._bFilesDropped = False
        self._bDuplicateRename = False

        #
        # Input Lines
        #
        self.textRegEx = RegExLineInputWidget(Text.txt0200, Text.txt0201)
        self.textSubString = RegExLineInputWidget(Text.txt0202, Text.txt0203)
        self.textOriginalNames = RegExFilesWidget(Text.txt0204, Text.txt0205)
        self.textOriginalNames.textBox.setReadOnly(True)
        self.textOriginalNames.textBox.connectToInsertText(
            self.outputOriginalFilesSignal
        )
        self.textOriginalNames.textBox.filesDroppedUpdateSignal.connect(
            self._setFilesDropped
        )
        self.textRenameResults = RegExInputWidget(Text.txt0206, Text.txt0207)
        self.textRenameResults.textBox.setReadOnly(True)
        self.textRenameResults.textBox.connectToInsertText(
            self.outputRenameResultsSignal
        )
        btnApplyRename = QPushButtonWidget(
            Text.txt0208,
            function=self._applyRename,
            margins="  ",
            toolTip=Text.txt0209,
        )
        btnApplyRename.setEnabled(False)
        btnUndoRename = QPushButtonWidget(
            Text.txt0210,
            function=self._undoRename,
            margins="  ",
            toolTip=Text.txt0211
        )
        btnUndoRename.setEnabled(False)
        btnClear = QPushButtonWidget(
            Text.txt0212,
            function=self.clear,
            margins="  ",
            toolTip=Text.txt0213
        )
        btnCalculateCRC = QPushButtonWidget(
            Text.txt0215, function=self._crc, margins=" ", toolTip=Text.txt0216
        )
        btnCalculateCRC.setEnabled(False)
        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnApplyRename)
        self.btnGrid.addWidget(btnUndoRename)
        self.btnGrid.addWidget(btnCalculateCRC)
        self.btnGrid.addStretch()
        self.btnGrid.addWidget(btnClear)
        self.btnGroup = QGroupBox()
        self.btnGroup.setLayout(self.btnGrid)

    def _initHelper(self):

        maxCount = config.data.get(Key.MaxRegExCount)
        # local signals
        # self.setCurrentIndexSignal.connect(self._setCurrentIndex)
        self.setFilesSignal.connect(self.setFiles)
        self.appendCRCSignal.connect(self.appendCRC)
        self.textRegEx.cmdLine.currentTextChanged.connect(self._updateRegEx)
        self.textSubString.cmdLine.currentTextChanged.connect(self._updateRegEx)
        self.textOriginalNames.textBox.textChanged.connect(self.clearButtonState)
        self.textRegEx.cmdLine.itemsChangeSignal.connect(
            lambda: self.saveItems(Key.RegEx)
        )
        self.textSubString.cmdLine.itemsChangeSignal.connect(
            lambda: self.saveItems(Key.SubString)
        )

        self.textOriginalNames.textBox.verticalScrollBar().valueChanged.connect(
            self.scrollRenameChanged
        )
        self.textRenameResults.textBox.verticalScrollBar().valueChanged.connect(
            self.scrollResultsChanged
        )

        if maxCount is not None:
            self.textRegEx.cmdLine.setMaxCount(maxCount)
            self.textSubString.cmdLine.setMaxCount(maxCount)
            items = config.data.get(Key.RegEx)
            self.textRegEx.cmdLine.addItems(items)
            self.textRegEx.cmdLine.clearEditText()
            items = config.data.get(Key.SubString)
            self.textSubString.cmdLine.addItems(items)
            self.textSubString.cmdLine.clearEditText()
        self.btnGrid.itemAt(ButtonIndex.Clear).widget().setEnabled(False)

    def _initUI(self):

        inputGrid = QGridLayout()
        #
        # Input lines
        #
        inputGrid.addWidget(self.textRegEx, 0, 0, 1, 2)
        inputGrid.addWidget(self.textSubString, 1, 0, 1, 2)
        # buttons
        inputGrid.addWidget(self.btnGroup, 2, 0, 1, 2)
        gridWidget = QWidget()
        gridWidget.setLayout(inputGrid)
        gridWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        boxWidget = QWidget()
        hboxLayout = QHBoxLayout()
        hboxLayout.addWidget(self.textOriginalNames)
        hboxLayout.addWidget(self.textRenameResults)
        boxWidget.setLayout(hboxLayout)
        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(gridWidget, 0, 0, 2, 0, Qt.AlignTop)
        grid.addWidget(boxWidget, 2, 0)
        self.setLayout(grid)

    def __bool__(self):
        for n, r in zip(self._originalFileNames, self._renameFileNames):
            if n != r:
                return True
        return False

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

        return RenameWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

    @Slot()
    def saveItems(self, comboType):
        """
        saveItems of ComboLineEdit use in widget

        Args:
            comboType (str): key indicating witch ComboListEdit
                             to save to config
        """

        if comboType == Key.RegEx:
            if self.textRegEx.cmdLine.count() > 0:
                items = []
                for i in range(0, self.textRegEx.cmdLine.count()):
                    items.append(self.textRegEx.cmdLine.itemText(i))
                config.data.set(Key.RegEx, items)
        if comboType == Key.SubString:
            if self.textRegEx.cmdLine.count():
                items = []
                for i in range(0, self.textSubString.cmdLine.count()):
                    items.append(self.textSubString.cmdLine.itemText(i))
                config.data.set(Key.SubString, items)

    @Slot(object)
    def setFiles(self, objCommand):
        """
        setFile setup file names to work with

        Args:
            objCommand (MKVCommand): MKVCommand object containing the files
                                     to rename
        """

        self.textOriginalNames.textBox.clear()
        self.textRenameResults.textBox.clear()
        self._originalFileNames = []
        self._bFilesDropped = False
        self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(False)

        for f in objCommand.destinationFiles:
            # show files
            self.outputOriginalFilesSignal.emit(str(f.name) + "\n", {})
            # save files
            self._originalFileNames.append(f)

        self._updateRegEx()

    @Slot(int)
    def scrollRenameChanged(self, value):
        self.textRenameResults.textBox.verticalScrollBar().valueChanged.disconnect(
            self.scrollResultsChanged
        )
        self.textRenameResults.textBox.verticalScrollBar().setValue(value)
        self.textRenameResults.textBox.verticalScrollBar().valueChanged.connect(
            self.scrollResultsChanged
        )

    @Slot(int)
    def scrollResultsChanged(self, value):
        self.textOriginalNames.textBox.verticalScrollBar().valueChanged.disconnect(
            self.scrollRenameChanged
        )
        self.textOriginalNames.textBox.verticalScrollBar().setValue(value)
        self.textOriginalNames.textBox.verticalScrollBar().valueChanged.connect(
            self.scrollRenameChanged
        )

    @Slot(int, Path)
    def appendCRC(self, index, name):

        try:
            self._renameFileNames[index] = name
            self.textRenameResults.textBox.clear()
            self._displayRenames()
            if self.log:
                MODULELOG.debug(
                    f"[RenameWidget.appendCRC] Update rename name "
                    f"index={index} to {name}"
                )
        except IndexError:
            if self.log:
                MODULELOG.debug(
                    f"[RenameWidget.appendCRC] Index out of bound "
                    f"index={index}."
                )

    def clear(self):
        """
        clear reset widget working variables and widgets
        """

        self._originalFileNames = []
        self._renameFileNames = []
        self._bFilesDropped = False
        self.textRegEx.cmdLine.lineEdit().clear()
        self.textSubString.cmdLine.lineEdit().clear()
        self.textOriginalNames.textBox.clear()
        self.textRenameResults.textBox.clear()

    def calculateCRCButtonState(self, state):
        self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(state)

    def clearButtonState(self):
        """Set clear button state"""

        if self.textOriginalNames.textBox.toPlainText() != "":
            self.btnGrid.itemAt(ButtonIndex.Clear).widget().setEnabled(True)
            #self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(ButtonIndex.Clear).widget().setEnabled(False)
            self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(False)
    @Slot()
    def undoButtonState(self):
        if not self._bFilesDropped:
            self.btnGrid.itemAt(ButtonIndex.Undo).widget().setEnabled(False)

    def connectToSetFiles(self, objSignal):

        objSignal.connect(self.setFiles)

    def translate(self):
        """
        setLanguage set labels according to locale
        """

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.translate()
                #widget.setText("  " + _(widget.originalText) + "  ")
                #widget.setToolTip(_(widget.toolTip))
        for w in [self.textRegEx, self.textSubString]:
            w.lblText.setText(_(w.label) + ": ")
            w.cmdLine.setToolTip(_(w.toolTip))
        for w in [self.textOriginalNames, self.textRenameResults]:
            w.lblText.setText(_(w.label) + ":")
            w.textBox.setToolTip(_(w.toolTip))
            w.repaint()

    def _setFilesDropped(self, filesDropped):

        if filesDropped:
            self._originalFileNames = []
            self._originalFileNames.extend(filesDropped)
            self.textRenameResults.textBox.clear()
            if not self._bFilesDropped:
                self._bFilesDropped = True
            self._updateRegEx()
            self.calculateCRCButtonState(True)
        else:
            # receive when clear issued to FilesListWidget
            self._originalFileNames = []
            self.textRenameResults.textBox.clear()
            self.btnGrid.itemAt(ButtonIndex.Undo).widget().setEnabled(False)
            self._bFilesDropped = False

    def _displayRenames(self):

        i = 0
        duplicateNames = findDuplicates(self._renameFileNames)
        if duplicateNames:
            self._bDuplicateRename = True
        else:
            self._bDuplicateRename = False
        for f in self._renameFileNames:
            of = Path(f)
            try:
                if (f in duplicateNames) or of.is_file():
                    self.outputRenameResultsSignal.emit(
                        str(f.name) + "\n", {"color": Qt.red}
                    )
                else:
                    # check theme
                    self.outputRenameResultsSignal.emit(str(f.name) + "\n", {})
                i = i + 1
            except OSError:
                self.outputRenameResultsSignal.emit(str(f.name) + "\n", {})

    def _updateRegEx(self):

        rg = self.textRegEx.cmdLine.currentText()
        subText = self.textSubString.cmdLine.currentText()
        statusBar = self.parent.statusBar()
        statusBar.showMessage("")
        self.textRenameResults.textBox.clear()
        self._renameFileNames = []
        try:
            regEx = re.compile(rg)
            for f in self._originalFileNames:
                strFile = f.stem
                matchRegEx = regEx.sub(subText, strFile)
                if matchRegEx:
                    objName = f.parent.joinpath(matchRegEx + f.suffix)
                else:
                    objName = f
                self._renameFileNames.append(objName)
            resolveIncrements(self._originalFileNames, self._renameFileNames, subText)
            self._displayRenames()
            if self:
                self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(True)
            else:
                self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(False)
        except re.error:
            self.textRenameResults.textBox.clear()
            statusBar.showMessage(Text.txt0214)

        if resolveIncrements(self._originalFileNames, self._renameFileNames, subText):
            self._displayRenames()
            if self:
                self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(True)
            else:
                self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(False)

    def _applyRename(self):

        if self._bFilesDropped:
            # self.applyFileRenameSignal.emit(self._renameFileNames)
            filesPair = zip(self._originalFileNames, self._renameFileNames)
            for oldName, newName in filesPair:
                try:
                    oldName.rename(newName)
                except FileExistsError:
                    pass
        else:
            self.applyFileRenameSignal.emit(self._renameFileNames)
        self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(False)
        self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(False)
        self.btnGrid.itemAt(ButtonIndex.Undo).widget().setEnabled(True)

    def _undoRename(self):

        if self._bFilesDropped:
            filesPair = zip(self._renameFileNames, self._originalFileNames)
            for oldName, newName in filesPair:
                try:
                    oldName.rename(newName)
                except FileExistsError:
                    pass
        else:
            self.applyFileRenameSignal.emit(self._originalFileNames)
        self.btnGrid.itemAt(ButtonIndex.ApplyRename).widget().setEnabled(True)
        self.btnGrid.itemAt(ButtonIndex.CalculateCRC).widget().setEnabled(True)
        self.btnGrid.itemAt(ButtonIndex.Undo).widget().setEnabled(False)

    def _crc(self, log):
        if self._bFilesDropped:

            for index, (currentName, newName) in \
                enumerate(zip(self._originalFileNames, self._renameFileNames)):

                crcWorker = ThreadWorker(
                    computeCRC,
                    updateName=self.appendCRCSignal,
                    index=index,
                    fileName=currentName,
                    newName=newName,
                    log=log
                )
                crcWorker.start()


def computeCRC(**kwargs: str) -> None:

    updateName = kwargs.pop("updateName", None)
    index = kwargs.pop("index", None)
    sourceFile = kwargs.pop("fileName", None)
    newName = kwargs.pop("newName", None)
    log = kwargs.pop("log", False)

    if sourceFile and newName:
        fileName = Path(sourceFile)
        newFileName = Path(newName)
        if fileName.is_file():
            crc = crc32(fileName.resolve())
            newNameWithCRC = appendCRC(newFileName, crc)
            updateName.emit(index, newNameWithCRC)
        else:
            if log:
                MODULELOG.error(f"[RenameWidget.computeCRC] File not found "
                        f"index={index} fileName={fileName}", index, fileName)
    else:
        if log:
            MODULELOG.debug(
                "[RenameWidget.computeCRC] Failed to get parameters.")


def appendCRC(fileName, crc) -> Path:

    name = str(fileName.resolve().stem)
    newNameCRC = None
    possibleCRC = False

    if len(name) >= 11:
        leftBracket = name[-10:-9]
        rightBracket = name[-1:]
        if (leftBracket == "[") and (rightBracket == "]"):
            testCRC = name[-9:-1]
            possibleCRC = bool(RenameWidget.reCrcChars.match(testCRC))

    if possibleCRC:
        # Already has crc remove it from name name[:-10]
        newName = name[:-10]
    else:
        # no crc detected use current name filename.stem
        newName = fileName.stem + ' '

    newNameCRC = (str(fileName.parent.resolve()) + "/" +
        newName + r"[" + crc + r"]" + fileName.suffix)

    result = None
    if newNameCRC is not None:
        result = Path(newNameCRC)

    return result


class ButtonIndex:

    ApplyRename = 0
    Undo = 1
    CalculateCRC = 2
    Clear = 4


class fileUnit:

    originalName = ""
    newName = ""
    crc = ""


class Key:

    RegEx = "RegEx"
    SubString = "SubString"
    MaxRegExCount = "MaxRegExCount"


# This if for Pylance _() is not defined
def _(dummy):
    return dummy


del _
