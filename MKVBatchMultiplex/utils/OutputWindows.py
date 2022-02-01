"""
OutputWindows class
"""

from PySide6.QtCore import QObject, Signal

from vsutillib.pyside6 import QOutputTextWidget

class OutputWindows(QObject):
    """
    OutputWindow class contain pointers to output windows inertText slots

    Args:
        outCommand 
    """

    command = Signal(str, dict)
    job = Signal(str, dict)
    error = Signal(str, dict)

    def __init__(
        self, 
        outCommand: QOutputTextWidget, 
        outJobs: QOutputTextWidget, 
        outError: QOutputTextWidget) -> None:

        super(OutputWindows, self).__init__()

        self.commandOutput = outCommand
        self.jobOutput = outJobs
        self.errorOutput = outError

        self.command.connect(outCommand.insertText)
        self.job.connect(outJobs.insertText)
        self.error.connect(outError.insertText)
