"""
Class to manage jobs.
"""

# JOB0001

import logging

from collections import deque

from PySide2.QtCore import QObject, QMutex, QMutexLocker, Qt, Slot, Signal

from vsutillib.mkv import MKVCommand

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
    AbortForced = "AbortForced"
    AbortJob = "AbortJob"
    AbortJobError = "AbortJobError"
    Blocked = "Blocked"


class JobInfo: # pylint: disable=R0903
    """
    Information related to a job

    :param status: initial job status defaults to empty string
    :type status: JobStatus
    :param command: command to execute in job
    :type command: str
    :param errors: errors execution or invalidating command
    :type errors: list
    :param output: output produce while executing command
    :type output: list
    """

    def __init__(self, status="", command=None, errors=None, output=None):

        self.status = status
        self.command = command
        self.errors = [] if (errors is None) else errors
        self.output = [] if (output is None) else output


class JobQueue(QObject): # pylint: disable=R0902
    """
    Class to manage jobs

    :param jobWorkQueue: set external queue for jobs
    :type jobWorkQueue: collections.deque
    """

    log = False
    jobID = 1
    outputJobSignal = Signal(str, dict)
    outputErrorSignal = Signal(str, dict)
    updateStatusSignal = Signal(int, str)
    addJobToTableSignal = Signal(int, str, str)

    def __init__(self, jobWorkQueue=None):
        super(JobQueue, self).__init__()

        if jobWorkQueue is None:
            self._workQueue = deque()
        else:
            self._workQueue = jobWorkQueue

        self._status = {}
        self._jobs = {}
        self._jobsStatus = None
        self.clearOutput = None
        self.emitError = False
        self.emitOutput = False
        self.emitStatusUpdates = False
        self.emitAddJobToTable = False

    def __bool__(self):
        if self._workQueue:
            return True
        return False

    def __len__(self):
        return len(self._jobs)

    def clear(self):
        """Clear the job queue"""

        self._workQueue.clear()

    def jobsStatus(self, setStatus=None):
        """
        Set or get job status this is mantained
        by qthProcessCommand

        :param setStatus: is value is sent set status to value
        :type setStatus: JobStatus
        """

        if setStatus is None:
            return self._jobsStatus

        self._jobsStatus = setStatus


    def abortAll(self):
        """abort any pending jobs"""

        for key, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                self.status(key, JobStatus.Aborted)

    def jobsAreWaiting(self):
        """
        check for waiting jobs

        :rtype: bool
        """

        for _, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                return True

        return False

    def jobsAreRunning(self):
        """
        check for running jobs

        :rtype: bool
        """

        for _, value in self._jobs.items():
            if value.status == JobStatus.Running:
                return True

        return False

    def requeueWaiting(self):
        """
        add any Wainting jobs to the job queue
        """

        for key, value in self._jobs.items():
            if value.status == JobStatus.Waiting:
                if not self.inQueue(value.command):
                    self._workQueue.append([key, value.command])

    def connectToStatus(self, objSignal):
        """
        Connect signal to status slot
        """

        objSignal.connect(self.status)

    @Slot(int, str, bool)
    def status(self, nID, strStatus=None, bUpdate=True):
        """
        Set/Return job status

        :param nID: job id
        :type nID: int
        :param strStatus: status to set if none return status
        :type strStatus: JobStatus
        :param bUpdate: update job table if True
        :type bUpdate: bool
        :rtype: JobStatus
        """

        if strStatus is None:
            if nID in self._jobs:
                return self._jobs[nID].status
            return ""

        self._jobs[nID].status = strStatus

        if self.emitStatusUpdates and bUpdate:
            self.updateStatusSignal.emit(nID, strStatus)

        return ""

    def append(self, command, status):
        """
        Add Job to end queue return assigned job id

        :param command: command to append
        :type command: str
        :param status: initial job status
        :type status: JobStatus
        :rtype: int
        """

        if isinstance(command, MKVCommand):
            cmd = command.command
            oCmd = command
        else:
            oCmd = None
            cmd = command

        with QMutexLocker(MUTEX):

            jobInfo = JobInfo()
            nID = self.jobID
            self.jobID += 1

            self._workQueue.append([nID, cmd, oCmd])

            jobInfo.status = status
            jobInfo.command = cmd
            self._jobs[nID] = jobInfo

            if self.emitAddJobToTable:
                self.addJobToTableSignal.emit(nID, status, cmd)

            return nID

    def appendLeft(self, command, status):
        """
        Add Job to front of queue

        :param command: command to append
        :type command: str
        :param status: initial job status
        :type status: JobStatus
        :rtype: int
        """

        if isinstance(command, MKVCommand):
            cmd = command.command
            oCmd = command
        else:
            oCmd = None
            cmd = command

        with QMutexLocker(MUTEX):

            nID = self.jobID
            jobInfo = JobInfo()
            self.jobID += 1

            self._workQueue.appendleft([nID, cmd, oCmd])
            jobInfo.status = status
            jobInfo.command = cmd
            self._jobs[nID] = jobInfo

            if self.emitAddJobToTable:
                self.addJobToTableSignal.emit(nID, status, cmd)

            return nID

    # Deque is thread safe
    def pop(self):
        """
        Retrieve element LIFO [job id, command]

        :rtype: list
        """

        if self._workQueue:
            return self._workQueue.pop()

        return [None, None, None]

    def popLeft(self):
        """
        Retrieve element FIFO [job id, command]

        :rtype: list
        """

        if self._workQueue:
            return self._workQueue.popleft()

        return [None, None, None]

    def inQueue(self, command):
        """
        Checks for command in queue

        :rtype: bool
        """

        for job in self._workQueue:
            if command == job[1]:
                return True

        return False

    def setOutputSignal(
            self,
            outputJobSlotConnection=None,
            outputErrorSlotConnection=None,
            addJobToTableSlotConnection=None,
            updateStatusSlotConnection=None,
            clearOutput=None
        ):
        """
        Setup output widget signals

        :param outputJobSlot: slot for job execution output
        :type outputJobSlot: Slot
        :param outputErrorSlot: slot for job execution errors
        :type outputErrorSlot: Slot
        :param addJobToTableSlot: slot for job table widget
        :type addJobToTableSlot: Slot
        :param updateStatusSlot: slot for job table status updates
        :type updateStatusSlot: Slot
        :param clearOutput: slot for clear output slot
        :type clearOutput: Slot
        """

        if outputJobSlotConnection:
            outputJobSlotConnection(self.outputJobSignal)
            self.emitOutput = True

        if outputErrorSlotConnection:
            outputErrorSlotConnection(self.outputErrorSignal)
            self.emitError = True

        if addJobToTableSlotConnection:
            addJobToTableSlotConnection(self.addJobToTableSignal)
            self.emitAddJobToTable = True

        if updateStatusSlotConnection:
            updateStatusSlotConnection(self.updateStatusSignal)
            self.emitStatusUpdates = True

        if clearOutput:
            self.clearOutput = clearOutput

    def outputJob(self, jobID, strMessage, dictAttributes, error=False):
        """Update job output on screen and save it"""

        if self.emitOutput:
            self.outputJobSignal.emit(
                strMessage,
                dictAttributes
            )

            if jobID in self._jobs:
                self._jobs[jobID].output.append([strMessage, dictAttributes])

        if error:
            self.outputError(jobID, strMessage, dictAttributes)

    def outputError(self, jobID, strMessage, dictAttributes):
        """Update job output on screen and save it"""

        if self.emitError:
            msg = "----------\nJob: {}\n\n{}\n----------\n\n"
            msg = msg.format(str(jobID), strMessage.strip())
            self.outputErrorSignal.emit(
                msg,
                dictAttributes
            )

            if jobID in self._jobs:
                self._jobs[jobID].errors.append([strMessage, dictAttributes])

    def connectToShowJobOutput(self, objSignal):
        """
        Connect to signals showJobOutput slot

        :param objSignal: signal to connect to
        :type: Signal
        """

        objSignal.connect(self.showJobOutput)

    @Slot(int, str, str)
    def showJobOutput(self, jobID, status, command): # pylint: disable=W0613
        """
        Click jobsWidget Table job row to update job run output and job error output

        :param jobID: job id
        :type jobID: int
        :param status: job status
        :type status: JobStatus
        :param command: command for job
        :type command: str
        """

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
