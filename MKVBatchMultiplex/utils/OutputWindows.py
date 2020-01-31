"""
OutputWindows class
"""

from PySide2.QtCore import QObject

class OutputWindow(QObject):

    outCommand = None
    outJobs = None
    outError = None

    def __init__(self, outCommand, outJobs, outError):
        super(OutputWindow, self).__init__()

        self.outCommand = outCommand
        self.outJobs = outJobs
        self.outError = outError
