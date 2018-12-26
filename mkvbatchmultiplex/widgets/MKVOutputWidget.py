#!/usr/bin/env python3

"""
MKVOutputWidget

Output Form

OW004
"""

import logging

from PyQt5.QtCore import QMutex, QMutexLocker, Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QTextEdit

MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVOutputWidget(QTextEdit):
    """Output for running queue"""

    def __init__(self, parent=None):
        super(MKVOutputWidget, self).__init__(parent)

        self.parent = parent

    def makeConnection(self, objSignal):
        """Connect to signal"""

        objSignal.connect(self.insertText)

    @pyqtSlot(str, dict)
    def insertText(self, strText, kwargs):
        """
        Insert text in output window
        Cannot use standard keyword argument kwargs
        on emit calls, use dictionary instead

        :param strText: text to insert on windows
        :type strText: str
        :param kwargs: dictionary for additional
        commands for the insert operation
        :type kwargs: dictionary
        """

        strTmp = ""

        with QMutexLocker(MUTEX):
            if 'color' in kwargs:
                color = kwargs['color']
            else:
                color = Qt.black

            if 'replaceLine' in kwargs:
                replaceLine = kwargs['replaceLine']
            else:
                replaceLine = False

            if replaceLine:
                self.moveCursor(QTextCursor.StartOfLine, 1)

            self.setTextColor(color)
            self.insertPlainText(strText)
            self.ensureCursorVisible()

            if self.parent.log:
                strTmp = strTmp + strText
                strTmp = strTmp.replace("\n", " ")
                if strTmp != "" and strTmp.find(u"Progress:") != 0:
                    if strTmp.find(u"Warning") == 0:
                        MODULELOG.warning("OW001: %s", strTmp)
                    elif strTmp.find(u"Error") == 0 or color == Qt.red:
                        MODULELOG.error("OW002: %s", strTmp)
                    else:
                        MODULELOG.info("OW003: %s", strTmp)
