"""
class CommandWidget
"""
import logging

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QGridLayout

from vsutillib.pyqt import OutputTextWidget

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(QWidget):
    """Output for running queue"""

    # log state
    __log = False
    insertText = Signal(str, dict)

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(self, parent=None):
        super(CommandWidget, self).__init__(parent)

        self.parent = parent
        self.outputWidget = OutputTextWidget(self)

        # map insertText signal to outputWidget one
        self.insertText = self.outputWidget.insertTextSignal

        self._initUI()

    def _initUI(self):

        grid = QGridLayout()

        grid.addWidget(self.outputWidget, 0, 0)

        self.setLayout(grid)

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return OutputTextWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value
