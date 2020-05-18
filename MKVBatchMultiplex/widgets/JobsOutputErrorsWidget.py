"""
JobsOutputWidget
"""

from vsutillib.pyqt import OutputTextWidget, TabWidgetExtension


class JobsOutputErrorsWidget(TabWidgetExtension, OutputTextWidget):

    def __init__(self, parent, log=None, **kwargs):
        super().__init__(parent=parent, log=log, **kwargs)

        self.parent = parent

    def clear(self):

        self.parent.progress.lblSetValue.emit(4, totalErrors)

        super().clear()
