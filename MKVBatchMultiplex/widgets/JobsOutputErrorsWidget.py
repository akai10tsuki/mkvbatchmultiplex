"""
JobsOutputWidget
"""

from typing import Optional, Any

from PySide6.QtWidgets import QWidget

from vsutillib.pyside6 import QOutputTextWidget, TabWidgetExtension


class JobsOutputErrorsWidget(TabWidgetExtension, QOutputTextWidget):

    def __init__(
        self,
        parent: QWidget,
        log: Optional[bool] = None,
        **kwargs: Any):
        super().__init__(parent=parent, log=log, **kwargs)
