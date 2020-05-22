"""
 convenience classes and functions used by RenameWidget

Returns:
    [type]: [description]

import logging
import re
import time

from pathlib import Path

from PySide2.QtCore import Signal, Qt, Slot
from PySide2.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QGroupBox,
)

import vsutillib.pyqt as pyqt
from vsutillib.process import isThreadRunning

from .. import config
"""

import re

from pathlib import Path

from PySide2.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget

from vsutillib.pyqt import QComboLineEdit, QOutputTextWidget, QFileListWidget

class RegExLineInputWidget(QWidget):
    """Input line with text labels"""

    def __init__(self, lblText="", strToolTip=""):
        super().__init__()

        self.label = lblText
        self.toolTip = strToolTip
        self.lblText = QLabel(lblText)
        self.cmdLine = QComboLineEdit(self)
        self.cmdLine.setToolTip(strToolTip)
        self.frmCmdLine = QFormLayout()
        self.frmCmdLine.addRow(self.lblText, self.cmdLine)
        self.frmCmdLine.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.setLayout(self.frmCmdLine)


class RegExInputWidget(QWidget):
    """Input box with text Labels"""

    def __init__(self, lblText="", strToolTip=""):
        super().__init__()

        self.label = lblText
        self.toolTip = strToolTip
        self.lblText = QLabel(lblText)
        self.textBox = QOutputTextWidget(self)
        self.textBox.setToolTip(strToolTip)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.lblText)
        vboxLayout.addWidget(self.textBox)
        self.setLayout(vboxLayout)


class RegExFilesWidget(QWidget):
    """Input for with text Labels"""

    def __init__(self, lblText="", strToolTip=""):
        super().__init__()

        self.label = lblText
        self.toolTip = strToolTip
        self.lblText = QLabel(lblText)
        self.textBox = QFileListWidget(self)
        self.textBox.setToolTip(strToolTip)
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.lblText)
        vboxLayout.addWidget(self.textBox)
        self.setLayout(vboxLayout)


def resolveIncrements(currentNames, newNames, subText):

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

    mGroups = matchGroups(subText, r"<i\:.*?(\d+)>")

    for item in zip(match, mGroups):
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
        if Path(fileNames[index]).parent == Path("."):
            nf = f.parent.joinpath(fileNames[index] + f.suffix)
        else:
            nf = Path(f)
        if bAppend:
            newNames.append(nf)
        else:
            newNames[index] = nf

    return True


def matchGroups(strText, strMatch):

    tmp = strText
    result = []
    reSearchEx = re.compile(strMatch)

    while True:
        matchGroup = reSearchEx.search(tmp)
        if matchGroup:
            group = matchGroup.group()
            result.append(group)
            tmp = re.sub(group, "", tmp)
        else:
            break

    return result


def findDuplicates(fileNames):

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
