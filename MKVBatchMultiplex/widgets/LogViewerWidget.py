"""
JobsOutputWidget
"""

import re

from typing import Optional, Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTextEdit, QWidget

from vsutillib.pyside6 import QOutputTextWidget, SvgColor, TabWidgetExtension


class LogViewerWidget(TabWidgetExtension, QOutputTextWidget):
    """
    LogViewerWidget widget to view running log
    This widget can be hidden on super().__init__ parent has to be None if not
    some glitches in main menu will show

    Args:
        TabWidgetExtension (widget): TabWidget child extensions
        QOutputTextWidget (widget): QTextEdit subclass use to show output generated
                                by running processes
    """

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        log: Optional[bool] = None,
        **kwargs: Any):
        super().__init__(parent=None, tabWidgetChild=self, **kwargs)

        self.parent = parent
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.reWords = re.compile(r"^(.*?) (.*?) (.*?) ")

    @Slot(object)
    def logMessage(self, msg):

        msgArgs = {"log": False}
        if matchWords := self.reWords.match(msg):
            logLevel = matchWords[3]
            if (logLevel == "DEBUG"):
                msgArgs = {"color": SvgColor.green, "log": False}
            elif (logLevel == "INFO"):
                msgArgs = {"color": SvgColor.white, "log": False}
            elif (logLevel == "WARNING"):
                msgArgs = {"color": SvgColor.yellow, "log": False}
            elif (logLevel == "ERROR"):
                msgArgs = {"color": SvgColor.red, "log": False}
            elif (logLevel == "CRITICAL"):
                msgArgs = {"color": SvgColor.orangered, "log": False}

        self.insertTextSignal.emit(msg + "\n", msgArgs)
