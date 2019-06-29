"""
MKVFormWidget:

Command input widget
"""

#LOG FW0013

import logging
import re

from pathlib import Path

from PySide2.QtCore import Signal, Qt, Slot
from PySide2.QtWidgets import (QGridLayout, QLabel, QWidget, QLineEdit,
                               QHBoxLayout, QVBoxLayout, QSizePolicy,
                               QPushButton, QGroupBox)

import vsutillib.pyqt as pyqt

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVRenameWidget(QWidget):
    """Central widget"""
    # pylint: disable=too-many-instance-attributes
    # Defining elements of a GUI

    outputRenameResultsSignal = Signal(str, dict)
    outputOriginalFileSignal = Signal(str, dict)
    applyFileRenameSignal = Signal(list)

    def __init__(self, parent):
        super(MKVRenameWidget, self).__init__(parent)

        self.parent = parent
        self._outputFileNames = []
        self._renameFileNames = []
        self._initControls()
        self._initLayout()
        self._bFilesDropped = False
        self._bDuplicateRename = False

    def _initControls(self):

        self.textFileName = RegExLineInputWidget(
            'Base File Name: ', 'Name parsed from command line.')
        self.textFileName.lineEdit.setReadOnly(True)
        self.textRegEx = RegExLineInputWidget("Regular Expression: ",
                                              'Enter regular expression.')
        self.textSubString = RegExLineInputWidget(
            "Substitution String: ", 'Enter substitution string.')
        self.textRegEx.lineEdit.textChanged.connect(self._updateRegEx)
        self.textSubString.lineEdit.textChanged.connect(self._updateRegEx)

        self.buttonApplyRename = QPushButton(' Apply Rename ')
        self.buttonApplyRename.resize(self.buttonApplyRename.sizeHint())
        self.buttonApplyRename.setSizePolicy(QSizePolicy.Fixed,
                                             QSizePolicy.Fixed)
        self.buttonApplyRename.clicked.connect(self._applyRename)
        self.buttonApplyRename.setEnabled(False)

        self.buttonUndoRename = QPushButton(' Undo ')
        self.buttonUndoRename.resize(self.buttonUndoRename.sizeHint())
        self.buttonUndoRename.setSizePolicy(QSizePolicy.Fixed,
                                            QSizePolicy.Fixed)
        self.buttonUndoRename.clicked.connect(self._undoRename)
        self.buttonUndoRename.setEnabled(False)

        self.textOriginalNames = RegExFilesWidget(
            self, "Original names:", "Name generated base on parsed command.")
        self.textOriginalNames.textBox.setReadOnly(True)
        self.textOriginalNames.textBox.connectToInsertText(
            self.outputOriginalFileSignal)
        self.textOriginalNames.textBox.filesDroppedUpdateSignal.connect(
            self._setOutputFilesDropped)

        self.textRenameResults = RegExInputWidget(
            self, "Rename:", "Names that will be use for commands.")
        self.textRenameResults.textBox.setReadOnly(True)
        self.textRenameResults.textBox.connectToInsertText(
            self.outputRenameResultsSignal)

    def _initLayout(self):

        btnGrid = QHBoxLayout()
        btnGrid.addWidget(self.buttonApplyRename)
        btnGrid.addWidget(self.buttonUndoRename)
        btnGrid.addStretch()

        btnGroup = QGroupBox()
        btnGroup.setLayout(btnGrid)

        inputGrid = QGridLayout()

        inputGrid.addWidget(self.textRegEx.lblText, 0, 0, Qt.AlignRight)
        inputGrid.addWidget(self.textSubString.lblText, 1, 0, Qt.AlignRight)

        inputGrid.addWidget(self.textRegEx.lineEdit, 0, 1)
        inputGrid.addWidget(self.textSubString.lineEdit, 1, 1)

        inputGrid.addWidget(btnGroup, 2, 0, 1, 2)

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

        for n, r in zip(self._outputFileNames, self._renameFileNames):
            if n != r:
                return True
        return False

    def clear(self):

        self._outputFileNames = []
        self._renameFileNames = []
        self._bFilesDropped = False

        self.textFileName.lineEdit.clear()
        self.textRegEx.lineEdit.clear()
        self.textSubString.lineEdit.clear()

        self.textOriginalNames.textBox.clear()
        self.textRenameResults.textBox.clear()

    def connectToSetOutputFile(self, objSignal):

        objSignal.connect(self.setOutputFile)

    @Slot(object)
    def setOutputFile(self, objCommand):

        self.textOriginalNames.textBox.clear()
        self.textRenameResults.textBox.clear()

        for f in objCommand.destinationFiles:
            # show files
            self.outputOriginalFileSignal.emit(str(f.name) + '\n', {})
            # save files
            self._outputFileNames.append(f)

    def _setOutputFilesDropped(self, filesDropped):

        if filesDropped:
            self._outputFileNames = []
            self._outputFileNames.extend(filesDropped)

            self.textRenameResults.textBox.clear()

            if not self._bFilesDropped:
                self._bFilesDropped = True

            self._updateRegEx()
        else:
            # receive when clear issued to FilesListWidget
            self._outputFileNames = []
            self.textRenameResults.textBox.clear()
            self.buttonUndoRename.setEnabled(False)
            self._bFilesDropped = False

    def _displayRenames(self):

        duplicateNames = _findDuplicates(self._renameFileNames)
        if duplicateNames:
            self._bDuplicateRename = True
        else:
            self._bDuplicateRename = False

        for f in self._renameFileNames:
            of = Path(f)
            if (f in duplicateNames) or of.is_file():
                self.outputRenameResultsSignal.emit(str(f.name) + '\n', {'color': Qt.red})
            else:
                self.outputRenameResultsSignal.emit(str(f.name) + '\n', {})

    def _updateRegEx(self):

        rg = self.textRegEx.lineEdit.text()
        subText = self.textSubString.lineEdit.text()
        statusBar = self.parent.statusBar()
        statusBar.showMessage("")
        self.textRenameResults.textBox.clear()
        self._renameFileNames = []

        try:
            regEx = re.compile(rg)
            for f in self._outputFileNames:
                strFile = f.stem
                matchRegEx = regEx.sub(subText, strFile)

                if matchRegEx:
                    objName = f.parent.joinpath(matchRegEx + f.suffix)
                else:
                    objName = f

                self._renameFileNames.append(objName)

            _resolveIncrements(self._outputFileNames, self._renameFileNames,
                               subText)

            self._displayRenames()

            if self:
                self.buttonApplyRename.setEnabled(True)
            else:
                self.buttonApplyRename.setEnabled(False)

        except re.error:

            self.textRenameResults.textBox.clear()
            statusBar.showMessage("Invalid regex.")

        if _resolveIncrements(self._outputFileNames, self._renameFileNames,
                              subText):
            self._displayRenames()

            if self:
                self.buttonApplyRename.setEnabled(True)
            else:
                self.buttonApplyRename.setEnabled(False)

    def _applyRename(self):

        if self._bFilesDropped:
            #self.applyFileRenameSignal.emit(self._renameFileNames)
            filesPair = zip(self._outputFileNames, self._renameFileNames)
            for oldName, newName in filesPair:
                try:
                    oldName.rename(newName)
                except FileExistsError:
                    pass

        else:
            self.applyFileRenameSignal.emit(self._renameFileNames)

        self.buttonApplyRename.setEnabled(False)
        self.buttonUndoRename.setEnabled(True)

    def _undoRename(self):

        if self._bFilesDropped:
            filesPair = zip(self._renameFileNames, self._outputFileNames)
            for oldName, newName in filesPair:
                try:
                    oldName.rename(newName)
                except FileExistsError:
                    pass
        else:
            self.applyFileRenameSignal.emit(self._outputFileNames)

        self.buttonApplyRename.setEnabled(True)
        self.buttonUndoRename.setEnabled(False)


class RegExLineInputWidget():
    """Input line with text labels"""

    def __init__(self, lblText="", strToolTip=""):
        super(RegExLineInputWidget, self).__init__()

        self.lblText = QLabel(lblText)
        self.lineEdit = QLineEdit()
        self.lineEdit.setToolTip(strToolTip)
        self.lineEdit.setClearButtonEnabled(True)


class RegExInputWidget(QWidget):
    """Input for with text Labels"""

    def __init__(self, parent=None, lblText="", strToolTip=""):
        super(RegExInputWidget, self).__init__(parent)

        self.lblText = QLabel(lblText)
        self.textBox = pyqt.OutputTextWidget(self)
        self.textBox.setToolTip(strToolTip)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.lblText)
        vboxLayout.addWidget(self.textBox)

        self.setLayout(vboxLayout)


class RegExFilesWidget(QWidget):
    """Input for with text Labels"""

    def __init__(self, parent=None, lblText="", strToolTip=""):
        super(RegExFilesWidget, self).__init__(parent)

        self.lblText = QLabel(lblText)
        self.textBox = pyqt.FileListWidget(self)
        self.textBox.setToolTip(strToolTip)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.lblText)
        vboxLayout.addWidget(self.textBox)

        self.setLayout(vboxLayout)


def _resolveIncrements(currentNames, newNames, subText):

    reSearchIncEx = re.compile(r"<i\:.*?(\d+)>")
    match = reSearchIncEx.findall(subText)
    fileNames = None
    bAppend = True

    if not match:
        return False

    # assume if for invalid regex
    fileNames = [subText] * len(currentNames)

    if newNames:
        bAppend = False
        testFNames = reSearchIncEx.findall(str(newNames[0]))

        # valid regex can duplicate index in rename name
        if testFNames and (len(match) == len(testFNames)):
            fileNames = []
            for f in newNames:
                fileNames.append(str(f))
        else:
            return False

    matchGroups = _matchGroups(subText, r"<i\:.*?(\d+)>")

    for item in zip(match, matchGroups):
        m, ii = item
        #    [int(m), "<i: NN>", "{:0" + str(len(m)) + "d}"]
        i = int(m)  # start index
        sf = "{:0" + str(len(m)) + "d}"  # string format for index

        for index, newName in enumerate(fileNames):
            # change increment index for string format in name n
            nName = re.sub(ii, sf, newName)
            nName = nName.format(i)  # change string format for index
            # substitute newName with substitution in index fileNames
            fileNames[index] = nName
            i += 1

    for index, f in enumerate(currentNames):
        # Path('.') is not full path use original name to get path
        if Path(fileNames[index]).parent == Path('.'):
            nf = f.parent.joinpath(fileNames[index] + f.suffix)
        else:
            nf = Path(f)

        if bAppend:
            newNames.append(nf)
        else:
            newNames[index] = nf

    return True


def _matchGroups(strText, strMatch):

    tmp = strText
    result = []
    reSearchEx = re.compile(strMatch)

    while True:
        matchGroup = reSearchEx.search(tmp)
        if matchGroup:
            group = matchGroup.group()
            result.append(group)
            tmp = re.sub(group, '', tmp)
        else:
            break

    return result


def _findDuplicates(fileNames):

    seen = {}
    duplicates = []

    if fileNames:
        for x in fileNames:
            if x not in seen:
                seen[x] = 1
            else:
                if seen[x] == 1:
                    duplicates.append(x)
                seen[x] += 1

    return duplicates
