"""
QValidator for command line
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QWidget

from vsutillib.mkv import VerifyMKVCommand

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class ValidateCommand(QValidator):
    """
    ValidateCommand class validates command line entered

    Args:
        parent (QWidget): parent widget
        resultSignal (Signal): Signal(bool) emitted when result found
        log (bool, optional): True do logging other value don't log.
                              Defaults to None.
    """

    __log = False

    def __init__(
            self,
            parent: QWidget,
            resultSignal: Signal,
            log: Optional[bool] = None):
        super().__init__(parent)

        self.parent = parent
        self.resultSignal = resultSignal
        self.__log = None
        self.log = log

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

        return ValidateCommand.classLog()

    @log.setter
    def log(self, value):
        """
        set instance log variable a value of None means class global
        logging state prevails.

        True or False overrides the class global state
        """
        if isinstance(value, bool) or value is None:
            self.__log = value

    @Slot(bool)
    def setLog(self, bLogging: bool) -> None:
        """Slot for setting loggin through signal"""
        self.log = bLogging

    # endregion Logging setup

    def validate(self, inputStr, pos):
        """Check regex in VerifyMKVCommand"""

        strTmp = inputStr

        if strTmp.find(r'^""') >= 0:
            strTmp = strTmp.strip()[1:-1].replace(r'""', r'"')

        verify = VerifyMKVCommand(strTmp, log=self.log)

        if verify:

            self.resultSignal.emit(True)

            if self.log:
                MODULELOG.debug("MCW0002: Command Ok: [%s]", strTmp)

        else:

            self.resultSignal.emit(False)

            if self.log:
                MODULELOG.debug("MCW0003: Command not Ok: [%s]", strTmp)

        return (QValidator.Acceptable, strTmp, pos)
