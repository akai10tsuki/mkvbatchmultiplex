"""
MKVFormWidget:

Command input widget
"""

#LOG FW0013

import logging
import re

from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import (QGridLayout, QLabel, QWidget, QLineEdit,
                               QHBoxLayout, QVBoxLayout, QSizePolicy)

from vsutillib.pyqt import OutputTextWidget
from ..utils import Text

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def _(s):  # pylint: disable=invalid-name
    """
    dummy function for pylint must be deleted when
    translations are needed
    """
    return s


class MKVRenameWidget(QWidget):
    """Central widget"""
    # pylint: disable=too-many-instance-attributes
    # Defining elements of a GUI

    outputMatchResultsSignal = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self._initControls()
        self._initLayout()

    def _initControls(self):

        self.textFileName = RegExLineInputWidget(
            'Base File Name: ', 'Name parsed from command line.')
        self.textRegEx = RegExLineInputWidget("Regular Expression: ",
                                              'Enter regular expression.')
        self.textSubString = RegExLineInputWidget(
            "Substitution String: ", 'Enter substitution string.')
        self.textRegEx.lineEdit.textChanged.connect(self._updateRegEx)
        self.textSubString.lineEdit.textChanged.connect(self._updateRegEx)
        self.textSubString.lineEdit.setReadOnly(True)

        self.textOriginalNames = RegExInputWidget(
            self, "Original names:", "Name generated base on parsed command.")
        self.textOriginalNames.textBox.setReadOnly(True)
        self.textOriginalNames.textBox.textChanged.connect(self._updateRegEx)

        self.textRenameResults = RegExInputWidget(
            self, "Rename:", "Names that will be use for commands.")
        self.textRenameResults.textBox.setReadOnly(True)
        self.textRenameResults.textBox.connectToInsertText(
            self.outputMatchResultsSignal)

    def _initLayout(self):

        gridWidget = QWidget()
        inputGrid = QGridLayout()

        inputGrid.addWidget(self.textFileName.lblText, 0, 0, Qt.AlignRight)
        inputGrid.addWidget(self.textRegEx.lblText, 1, 0, Qt.AlignRight)
        inputGrid.addWidget(self.textSubString.lblText, 2, 0, Qt.AlignRight)

        inputGrid.addWidget(self.textFileName.lineEdit, 0, 1)
        inputGrid.addWidget(self.textRegEx.lineEdit, 1, 1)
        inputGrid.addWidget(self.textSubString.lineEdit, 2, 1)

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

    def _updateRegEx(self):

        rg = self.textRegEx.lineEdit.text()
        subText = self.textSubString.lineEdit.text()
        strText = self.textOriginalNames.textBox.toPlainText()
        statusBar = self.parent.statusBar()

        try:

            regEx = re.compile(rg)
            matchRegEx = regEx.sub(subText, strText)
            bOk = True
            statusBar.showMessage("")
            self.textRenameResults.textBox.clear()

        except re.error:

            bOk = False

        if bOk:

            if matchRegEx:
                print('sub line by line')


        else:

            self.textRenameResults.textBox.clear()
            statusBar.showMessage(_(Text.txt0011))

    def setLanguage(self, initLanguage=False):
        """
        assign text labels in current language
        """

        if initLanguage:
            del globals()['_']

        self.textRegEx.lblText.setText(_(Text.txt0005) + ': ')
        self.textRegEx.lineEdit.setToolTip(_(Text.txt0006))
        self.textSubString.lblText.setText(_(Text.txt0007) + ': ')
        self.textSubString.lineEdit.setToolTip(_(Text.txt0008))

        self.textOriginalNames.lblText.setText(_(Text.txt0009) + ':')
        self.textOriginalNames.textBox.setToolTip(_(Text.txt0010))

        self.textRenameResults.lblText.setText(Text.txt0034(1) + ':')
        self.textRenameResults.textBox.setToolTip(_(Text.txt0012))


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
        self.textBox = OutputTextWidget(self)
        self.textBox.setToolTip(strToolTip)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.lblText)
        vboxLayout.addWidget(self.textBox)

        self.setLayout(vboxLayout)
