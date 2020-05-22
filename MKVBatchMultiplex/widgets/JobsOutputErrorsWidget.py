"""
JobsOutputWidget
"""

from vsutillib.pyqt import QOutputTextWidget, TabWidgetExtension


class JobsOutputErrorsWidget(TabWidgetExtension, QOutputTextWidget):

    def __init__(self, parent, log=None, **kwargs):
        super().__init__(parent=parent, log=log, **kwargs)

        self.parent = parent

    def clear(self):

        self.parent.progress.lblSetValue.emit(4, 0)

        super().clear()
