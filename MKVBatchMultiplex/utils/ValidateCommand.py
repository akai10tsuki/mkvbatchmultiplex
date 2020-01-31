"""
QValidator for command line
"""

import logging

from PySide2.QtGui import QValidator

from vsutillib import mkv

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class ValidateCommand(QValidator):
    """Validate command line entered"""

    def __init__(self, parent, resultSignal):
        super(ValidateCommand, self).__init__(parent)

        self.parent = parent
        self.resultSignal = resultSignal

    def validate(self, inputStr, pos):
        """Check regex in VerifyMKVCommand"""

        verify = mkv.VerifyMKVCommand(inputStr)

        if verify:

            self.resultSignal.emit(True)

            if self.parent.log:
                MODULELOG.debug("MCW0002: Command Ok: [%s]", inputStr)

        else:

            self.resultSignal.emit(False)

            if self.parent.log:
                MODULELOG.debug("MCW0003: Command not Ok: [%s]", inputStr)

        return (QValidator.Acceptable, inputStr, pos)
