"""
QNewWidget Class: Description

"""
# Next Log ID: LOG0001

import logging

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QGroupBox, QWidget

from vsutillib.pyside6 import TabWidgetExtension

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class QNewWidget(TabWidgetExtension, QWidget):
    """Widget Description"""

    # logging state
    __log = False

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            title: Optional[str] = None,
            log: Optional[bool] = None) -> None:
        super().__init__(parent=parent, tabWidgetChild=self)

        self.parent = parent
        self.__log = None
        self.log = log

        self._initVars()
        self._initUI(title)
        self._initHelper()

    def _initVars(self):
        pass # Pending implementation

    def _initUI(self, title):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(title)

        #
        # Widget controls definition
        #

        self.grpBox.setLayout(self.grpGrid)

        grid.addWidget(self.grpBox)
        self.setLayout(grid)

    def _initHelper(self):
        pass # Pending implementation

    # region Logging setup

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

        return QNewWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @Slot(bool)
    def setLog(self, bLogging: bool) -> None:
        """Slot for setting loggin through signal"""
        self.log = bLogging

    # endregion Logging setup
