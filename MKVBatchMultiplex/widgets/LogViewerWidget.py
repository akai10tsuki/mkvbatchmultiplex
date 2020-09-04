"""
JobsOutputWidget
"""

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QTextEdit

from vsutillib.pyqt import QOutputTextWidget, TabWidgetExtension


class LogViewerWidget(TabWidgetExtension, QOutputTextWidget):
    """
    LogViewerWidget widget to view running log

    Args:
        TabWidgetExtension (widget): TabWidget child extensions
       QOutputTextWidget (widget): QTextEdit subclass use to show output generated
                                by running processes
    """

    def __init__(self, parent=None, log=None, **kwargs):
        super().__init__(parent=parent, tabWidgetChild=self, **kwargs)

        self.setReadOnly(True)
        self.setLineWrapColumnOrWidth(QTextEdit.NoWrap)

    @Slot(object)
    def logMessage(self, msg):

        self.insertTextSignal.emit(msg + "\n", {"log": False})
