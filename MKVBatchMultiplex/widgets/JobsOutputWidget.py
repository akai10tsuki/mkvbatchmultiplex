"""
JobsOutputWidget
"""

from vsutillib.pyqt import OutputTextWidget, TabWidgetExtension


class JobsOutputWidget(TabWidgetExtension, OutputTextWidget):

    def __init__(self, parent=None, log=None, **kwargs):
        super().__init__(parent=parent, log=log, **kwargs)
