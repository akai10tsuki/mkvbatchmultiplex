"""
 Jobs class to manage jobs queue
"""
# JOB0001

import logging

from collections import deque

from PySide2.QtCore import QObject, Slot, Signal

from vsutillib.mkv import MKVCommand

from .. import config
from ..models import TableProxyModel
from .jobKeys import JobStatus
from .RunJobs import RunJobs


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())
JOBID, JOBSTATUS, JOBCOMMAND = range(3)


class JobInfo:  # pylint: disable=R0903
    """
    JobInfo Information for a job

    Args:
        status (str, optional): job status. Defaults to "".
        index ([type], optional): index on job table. Defaults to None.
        job (list, optional): row on job table. Defaults to None.
        errors (list, optional): errors on job execution. Defaults to None.
        output (list, optional): job output. Defaults to None.
    """

    def __init__(self, index=None, job=None, errors=None, output=None):

        self.jobIndex = index[config.JOBID]
        self.statusIndex = index[config.JOBSTATUS]
        self.commandIndex = index[config.JOBCOMMAND]
        self.job = job
        self.command = job[config.JOBCOMMAND]
        self.oCommand = MKVCommand(job[config.JOBCOMMAND])
        self.errors = [] if errors is None else errors
        self.output = [] if output is None else output


class JobQueue(QObject):
    """
    __init__ JobQueue - manage jobs

    Args:
        jobWorkQueue (collections.dequeue, optional): set external dequeue. Defaults to None.
    """

    # Class logging state
    __log = False

    __jobID = 10

    statusUpdateSignal = Signal(object, str)
    runSignal = Signal()
    addQueueItemSignal = Signal()
    queueEmptiedSignal = Signal()

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

    def __init__(self, parent, model=None, funcProgress=None, jobWorkQueue=None):
        super(JobQueue, self).__init__(parent)

        self.__progress = None
        self.parent = parent
        self.tableModel = model
        self.progress = funcProgress

        if jobWorkQueue is None:
            self._workQueue = deque()
        else:
            self._workQueue = jobWorkQueue

        self.runJobs = RunJobs(self, self) # progress function is a late bind

        self.statusUpdateSignal.connect(self.statusUpdate)
        self.runSignal.connect(self.run)

    def __bool__(self):
        if self._workQueue:
            return True
        return False

    def __len__(self):
        return len(self._workQueue)

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

        return JobQueue.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @property
    def model(self):
        return self.tableModel

    @model.setter
    def model(self, value):
        if isinstance(value, TableProxyModel):
            self.tableModel = value.sourceModel()

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    @model.setter
    def model(self, value):
        if isinstance(value, TableProxyModel):
            self.tableModel = value.sourceModel()

    @Slot(object, str)
    def statusUpdate(self, job, status):

        self.tableModel.setData(job.statusIndex, status)

    def append(self, jobRow):
        """
        append append job to queue

        Args:
            index (QModelIndex): index for job status on dataset
            job (list): job row on dataset

        Returns:
            bool: True if append successful False otherwise
        """

        job = self.tableModel.dataset[jobRow, ]
        status = job[config.JOBSTATUS]
        if status != JobStatus.AddToQueue:
            return False

        jobID = job[config.JOBID]
        jobIndex = self.tableModel.index(jobRow, JOBID)
        statusIndex = self.tableModel.index(jobRow, JOBSTATUS)
        commandIndex = self.tableModel.index(jobRow, JOBCOMMAND)

        newJob = JobInfo([jobIndex, statusIndex, commandIndex], job)
        self._workQueue.append(newJob)

        if not jobID:
            self.tableModel.setData(jobIndex, self.__jobID)
            self.__jobID += 1

        self.tableModel.setData(statusIndex, JobStatus.Queue)

        if self._workQueue:
            self.addQueueItemSignal.emit()
            return True

        return False

    def clear(self):
        """Clear the job queue"""

        while job := self.pop():
            print("Clearing the way {}".format(job.job[config.JOBID]))

    def popLeft(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            return self._workQueue.popleft()

        return None

    def popRight(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            return self._workQueue.pop()

        return None

    def pop(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            return self._workQueue.pop()

        return None

    @Slot()
    def run(self):
        """
        run test run worker thread
        """
        self.runJobs.progress  = self.progress
        self.runJobs.run()
