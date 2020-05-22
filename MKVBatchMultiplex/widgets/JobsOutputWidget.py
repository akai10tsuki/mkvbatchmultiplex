"""
JobsOutputWidget
"""

from vsutillib.pyqt import QOutputTextWidget, TabWidgetExtension


class JobsOutputWidget(TabWidgetExtension, QOutputTextWidget):

    def __init__(self, parent=None, log=None, **kwargs):
        super().__init__(parent=parent, log=log, **kwargs)
