"""
MKVOutputWidget:

Output widget form just to output text in color

"""
# OW004


import logging

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import QTextEdit

from .. import utils


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

        color = None
        replaceLine = False
        appendLine = False

        if 'color' in kwargs:
            color = kwargs['color']

        if 'replaceLine' in kwargs:
            replaceLine = kwargs['replaceLine']

        if 'appendLine' in kwargs:
            appendLine = kwargs['appendLine']

        if utils.isMacDarkMode() and (color is None):
            color = Qt.white
        elif color is None:
            color = Qt.black

        if color is not None:
            # dark theme clash
            self.setTextColor(color)

        if replaceLine:
            self.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            self.insertPlainText(strText)
        elif appendLine:
            self.append(strText)
        else:
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
