"""
Define different signals for progress updates
"""

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from vsutillib.pyside6 import DualProgressBar, QFormatLabel


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

    def __init__(
            self,
            parent: QWidget,
            progressBar: QWidget,
            formatLabel: Optional[QWidget] = None) -> None:
        super(Progress, self).__init__()

        self.parent = parent
        self.pb = progressBar
        self.lbl = formatLabel

        if formatLabel is not None:
            self._initHelper(True, True)
        else:
            self._initHelper(True, False)

    def _initHelper(
            self,
            initProgressBar: Optional[bool] = False,
            initLabel: Optional[bool] = False) -> None:

        if initProgressBar:

            # reset was use for the taskbar button that is no longer available
            #self.pbReset.connect(self.pb.clear)
            self.pbSetAlignment.connect(self.pb.setAlignment)
            self.pbSetValues.connect(self.pb.setValues)
            self.pbSetMaximum.connect(self.pb.setMaximum)
            self.pbSetMinimum.connect(self.pb.setMinimum)
            self.pbSetRange.connect(self.pb.setRange)

        if initLabel:

            self.lblSetValue.connect(self.lbl.setValue)
            self.lblSetValues.connect(self.lbl.setValues)

    @property
    def progressBar(self) -> DualProgressBar:
        return self.pb

    @progressBar.setter
    def progressBar(self, value) -> None:

        if isinstance(value, DualProgressBar):
            self.pb = value

    @property
    def formatLabel(self) -> QFormatLabel:
        return self.lbl

    @formatLabel.setter
    def formatLabel(self, value):
        if isinstance(value, QFormatLabel):
            self.lbl = value
