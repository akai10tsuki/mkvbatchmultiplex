"""
CommandWidget Class: Class to read the mkvtoolnix-gui command

"""
# Next Log ID: CMD0001

import logging

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGridLayout,
    QLineEdit,
    QWidget,
)

from vsutillib.pyside6 import (
    QPushButtonWidget,
)

from .. import config
from ..utils import Text

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class CommandWidget(QWidget):
    """Widget Description"""

    # logging state
    __log = False

    # signals
    updateCommandSignal = Signal(str)

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            log: Optional[bool] = None) -> None:
        super().__init__(parent=parent)

        self.parent = parent
        self.__log = None
        self.log = log

        self._initVars()
        self._initHelper()
        self._initUI()

    def _initVars(self):
        #
        # command line
        #
        self.frmCommandLine = QFormLayout()
        self.commandLine = QLineEdit()
        self.commandWidget = QWidget()

    def _initHelper(self):

        # region command line
        btnPasteClipboard = QPushButtonWidget(
            Text.txt0164,
            function=self.pasteClipboard,
            margins="  ",
            toolTip=Text.txt0165,
        )
        self.frmCommandLine.addRow(btnPasteClipboard, self.commandLine)
        self.frmCommandLine.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow)

        # self.commandLine.setValidator(
        #    ValidateCommand(self, self.cliValidateSignal, log=self.log)
        # )
        # button at end of line to clear it
        self.commandLine.setClearButtonEnabled(True)

        self.commandWidget.setLayout(self.frmCommandLine)
        self.updateCommandSignal.connect(self.updateCommand)
        # endregion

    def _initUI(self):
        
        grid = QGridLayout()
        grid.addWidget(self.commandWidget, 0, 0, 1, 2)

        self.setLayout(grid)

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

        return CommandWidget.classLog()

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

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        clip = QApplication.clipboard().text()

        if clip:
            # self.output.command.emit(
            #    "Checking command...\n", {LineOutput.AppendEnd: True}
            # )
            self.update()
            self.updateCommandSignal.emit(clip)

    @Slot(str)
    def updateCommand(self, command):
        """Update command input widget"""

        self.commandLine.clear()
        self.commandLine.setText(command)
        self.commandLine.setCursorPosition(0)

    @Slot()
    def setLanguage(self):
        """
        Set language used in buttons/lables called in MainWindow
        """

        for index in range(self.frmCommandLine.rowCount()):
            widget = self.frmCmdLine.itemAt(index, QFormLayout.LabelRole).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setLanguage() 