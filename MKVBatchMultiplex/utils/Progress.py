"""
Define different signals for progress updates
"""

from PySide2.QtCore import QObject, Signal

from vsutillib.pyqt import DualProgressBar, QFormatLabel


class Progress(QObject):
    """
    Progress class to connect Signals to DualProgressBar and QFormatLabel classes

    Args:
        parent (QWidget): parent widget
        progressBar (DualProgressBar): progress bar widget
        formatLabel (QFormatLabel, optional): label with text defined as
                                             a format string.
            Defaults to None.
    """

    pbReset = Signal()
    pbSetAlignment = Signal(int)
    pbSetValues = Signal(int, int)
    pbSetMaximum = Signal(int, int)
    pbSetMinimum = Signal(int, int)
    pbSetRange = Signal(int, int, int, int)
    lblSetValues = Signal(list)
    lblSetValue = Signal(int, object)

    def __init__(self, parent, progressBar, formatLabel=None):
        super(Progress, self).__init__()

        self.parent = parent
        self.pb = progressBar
        self.lbl = formatLabel

        if formatLabel is not None:
            self._initHelper(True, True)
        else:
            self._initHelper(True, False)

    def _initHelper(self, initProgressBar=False, initLabel=False):

        if initProgressBar:

            self.pbReset.connect(self.pb.reset)
            self.pbSetAlignment.connect(self.pb.setAlignment)
            self.pbSetValues.connect(self.pb.setValues)
            self.pbSetMaximum.connect(self.pb.setMaximum)
            self.pbSetMinimum.connect(self.pb.setMinimum)
            self.pbSetRange.connect(self.pb.setRange)

        if initLabel:

            self.lblSetValue.connect(self.lbl.setValue)
            self.lblSetValues.connect(self.lbl.setValues)

    @property
    def progressBar(self):
        return self.pb

    @progressBar.setter
    def progressBar(self, value):

        if isinstance(value, DualProgressBar):
            self.pb = value

    @property
    def formatLabel(self):
        return self.lbl

    @formatLabel.setter
    def formatLabel(self, value):
        if isinstance(value, QFormatLabel):
            self.lbl = value
