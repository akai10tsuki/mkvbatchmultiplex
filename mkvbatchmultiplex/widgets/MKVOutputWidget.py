#!/usr/bin/env python3

"""
MKVOutputWidget

Output Form

OW004
"""

import logging

from PySide2.QtCore import QMutex, QMutexLocker, Qt, Slot
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QTextEdit

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

    @Slot(str, dict)
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
            color = None
            replaceLine = False

            if 'color' in kwargs:
                color = kwargs['color']

            if 'replaceLine' in kwargs:
                replaceLine = kwargs['replaceLine']

            if replaceLine is not None:
                self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)

            if color is not None:
                # dark theme clash
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
