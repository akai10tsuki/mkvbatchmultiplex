#!/usr/bin/env python3

"""
Class to manage jobs.
"""

import logging

from collections import deque

from PyQt5.QtCore import QObject, QMutex, QMutexLocker, Qt, pyqtSlot, pyqtSignal


MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobStatus: # pylint: disable=R0903
    """Actions for context menu"""

    Abort = "Abort"
    Aborted = "Aborted"
    Done = "Done"
    Running = "Running"
    Skip = "Skip"
    Stop = "Stop"
    Waiting = "Waiting"
    Error = "Error"


class JobInfo: # pylint: disable=R0903
    """Information related to a Job"""

    def __init__(self, status="", command=None, errors=None, output=None):

        self.status = status
        self.command = command
        self.errors = [] if (errors is None) else errors
        self.output = [] if (output is None) else output


class JobQueue(QObject): # pylint: disable=R0902
    """Jobs class"""

    jobID = 1
    outputJobSignal = pyqtSignal(str, dict)
    outputErrorSignal = pyqtSignal(str, dict)
    updateStatusSignal = pyqtSignal(int, str)
    addJobToTableSignal = pyqtSignal(int, str, str)

    def __init__(self, jobWorkQueue=None):
        super(JobQueue, self).__init__()

        if jobWorkQueue is None:
            self._workQueue = deque()
        else:
            self._workQueue = jobWorkQueue

        self._status = {}
        self._jobs = {}
        self.clearOutput = None
        self.emitError = False
        self.emitOutput = False
        self.emitStatusUpdates = False
        self.emitAddJobToTable = False

    def __bool__(self):
        if self._workQueue:
            return True

        return False

    def clear(self):
        """Clear the job queue"""

        self._workQueue.clear()

    def abortAll(self):
        """abort any pending jobs"""

        for key, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                self.status(key, JobStatus.Aborted)

    def jobsAreWaiting(self):
        """check for waiting jobs"""

        for _, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                return True

        return False

    def jobsAreRunning(self):
        """check for running jobs"""

        for _, value in self._jobs.items():
            if value.status == JobStatus.Running:
                return True

        return False

    def requeueWaiting(self):
        """abort any pending jobs"""

        for key, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                if not self.inQueue(value.command):
                    self._workQueue.append([key, value.command])

    def connectToStatus(self, objSignal):
        """Connect to status slot"""

        objSignal.connect(self.status)

    @pyqtSlot(int, str, bool)
    def status(self, nID, strStatus=None, bUpdate=True):
        """Return/Set job status"""

        if strStatus is None:
            if nID in self._jobs:
                return self._jobs[nID].status
            return ""

        #print("Update job = {} status = {}".format(nID, strStatus))

        self._jobs[nID].status = strStatus

        if self.emitStatusUpdates and bUpdate:
            #print("Update table job = {} status = {}".format(nID, strStatus))
            self.updateStatusSignal.emit(nID, strStatus)

        return ""

    def append(self, command, status):
        """Add Job to End Queue"""

        with QMutexLocker(MUTEX):

            jobInfo = JobInfo()
            nID = self.jobID
            self.jobID += 1

            self._workQueue.append([nID, command])
            jobInfo.status = status
            jobInfo.command = command
            self._jobs[nID] = jobInfo

            if self.emitAddJobToTable:
                self.addJobToTableSignal.emit(nID, status, command)

            return nID

    def appendLeft(self, command, status=None):
        """Add Job to Front of Queue"""

        with QMutexLocker(MUTEX):

            nID = self.jobID
            jobInfo = JobInfo()
            self.jobID += 1

            self._workQueue.appendleft([nID, command])
            jobInfo.status = status
            self._jobs[nID] = jobInfo

            if self.emitAddJobToTable:
                self.addJobToTableSignal.emit(nID, command)

            return nID

    # Deque is thread safe
    def pop(self):
        """Retrieve element LIFO"""

        if self._workQueue:
            return self._workQueue.pop()

        return [None, None]

    def popLeft(self):
        """Retrieve element FIFO"""

        if self._workQueue:
            return self._workQueue.popleft()

        return [None, None]

    def inQueue(self, command):
        """Checks for command in queue"""

        for job in self._workQueue:
            if command == job[1]:
                return True

        return False

    def setOutputSignal(self, outputJobSlot=None, outputErrorSlot=None,      # pylint: disable=R0913
                        addJobToTableSlot=None, updateStatusSlot=None,
                        clearOutput=None):
        """Setup output widget signals"""

        if outputJobSlot:
            outputJobSlot(self.outputJobSignal)
            self.emitOutput = True

        if outputErrorSlot:
            outputErrorSlot(self.outputErrorSignal)
            self.emitError = True

        if addJobToTableSlot:
            addJobToTableSlot(self.addJobToTableSignal)
            self.emitAddJobToTable = True

        if updateStatusSlot:
            updateStatusSlot(self.updateStatusSignal)
            self.emitStatusUpdates = True

        if clearOutput:
            self.clearOutput = clearOutput

    def outputJob(self, jobID, strMessage, dictAttributes):
        """Update job output on screen and save it"""

        if self.emitOutput:
            self.outputJobSignal.emit(
                strMessage,
                dictAttributes
            )

            if jobID in self._jobs:
                self._jobs[jobID].output.append([strMessage, dictAttributes])

    def outputError(self, jobID, strMessage, dictAttributes):
        """Update job output on screen and save it"""

        if self.emitError:
            self.outputErrorSignal.emit(
                strMessage,
                dictAttributes
            )

            if jobID in self._jobs:
                self._jobs[jobID].errors.append([strMessage, dictAttributes])

    def makeConnection(self, objSignal):
        """Connect to signals"""

        objSignal.connect(self.showJobOutput)

    @pyqtSlot(int, str, str)
    def showJobOutput(self, jobID, status, command): # pylint: disable=W0613
        """Click jobsWidget Table Slot"""

        if jobID and (self.emitOutput or self.emitError):

            self.clearOutput()

            if self.emitOutput:
                self.outputJobSignal.emit(
                    "Job {} - {}\n\n".format(jobID, command),
                    {'color': Qt.blue}
                )
                for line in self._jobs[jobID].output:
                    self.outputJobSignal.emit(
                        line[0],
                        line[1]
                    )

            if self.emitError:
                self.outputErrorSignal.emit(
                    "Job {}\n\n".format(jobID),
                    {'color': Qt.blue}
                )
                for line in self._jobs[jobID].errors:
                    self.outputErrorSignal.emit(
                        line[0],
                        line[1]
                    )
