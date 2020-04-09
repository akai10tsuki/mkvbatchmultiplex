"""
OutputWindows class
"""

from PySide2.QtCore import QObject, Signal

class OutputWindows(QObject):
    """
    OutputWindow class contain pointers to output windows inertText slots

    Args:
        QObject ([type]): [description]
    """

    command = Signal(str, dict)
    job = Signal(str, dict)
    error = Signal(str, dict)

    def __init__(self, outCommand, outJobs, outError):
        super(OutputWindows, self).__init__()

        self.commandOutput = outCommand
        self.jobOutput = outJobs
        self.errorOutput = outError

        self.command.connect(outCommand.insertText)
        self.job.connect(outJobs.insertText)
        self.error.connect(outError.insertText)
