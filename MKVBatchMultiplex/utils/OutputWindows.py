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

    def __init__(self, outCommandInsertText, outJobsInsertText, outErrorInsertText):
        super(OutputWindows, self).__init__()

        self.command.connect(outCommandInsertText)
        self.job.connect(outJobsInsertText)
        self.error.connect(outErrorInsertText)
