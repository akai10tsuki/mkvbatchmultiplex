"""
JobsOutputWidget
"""

from typing import Optional, Any

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTextEdit, QWidget

from vsutillib.pyside6 import QOutputTextWidget, TabWidgetExtension


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
        self.setLineWrapColumnOrWidth(QTextEdit.LineWrapMode.NoWrap.value)

    @Slot(object)
    def logMessage(self, msg):

        self.insertTextSignal.emit(msg + "\n", {"log": False})
