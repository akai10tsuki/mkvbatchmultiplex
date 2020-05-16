"""
 Jobs class to manage jobs queue
"""
# JOB0001

# pylint: disable=bad-continuation

import copy
import logging

from collections import deque
from datetime import datetime
from time import time

from PySide2.QtCore import QObject, Slot, Signal


from vsutillib.mkv import MKVCommand, MKVCommandParser

from .. import config
from ..models import TableProxyModel
from .jobKeys import JobStatus, JobKey
from .RunJobs import RunJobs


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

class FakeModelIndex:
    """
    Dummy QModelIndex

    Returns:
        Index: Dummy QModelIndex
    """

    def __init__(self, row, column):

        self._row = row
        self._column = column

    def row(self):
        return self._row

    def column(self):
        return self._column

    def isValid(self):
        return True

class JobInfo:  # pylint: disable=too-many-instance-attributes
    """
    JobInfo Information for a job

    Args:
        status (str, optional): job status. Defaults to "".
        index ([type], optional): index on job table. Defaults to None.
        job (list, optional): row on job table. Defaults to None.
        errors (list, optional): errors on job execution. Defaults to None.
        output (list, optional): job output. Defaults to None.
    """

    def __init__(
        self, index, job, tableModel, errors=None, output=None, log=False,
    ):

        self.jobIndex = index[JobKey.ID]
        self.statusIndex = index[JobKey.Status]
        self.commandIndex = index[JobKey.Command]
        self.job = job
        self.command = job[JobKey.Command]
        self.oCommand = copy.deepcopy(
            tableModel.dataset.data[self.commandIndex.row()][
                self.commandIndex.column()
            ].oCommand
        )

        if not self.oCommand:
            # self.oCommand = MKVCommand(job[JobKey.Command], log=log)
            self.oCommand = MKVCommandParser(job[JobKey.Command], log=log)
            print("Bad oCommand found!!")

        self.date = datetime.today()
        self.addTime = time()
        self.startTime = None
        self.stopTime = None
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

    __firstRun = True
    __jobID = 10

    statusUpdateSignal = Signal(object, str)
    runSignal = Signal()
    addQueueItemSignal = Signal()
    addWaitingItemSignal = Signal()
    queueEmptiedSignal = Signal()
    statusChangeSignal = Signal(object)

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

    def __init__(
        self,
        parent,
        proxyModel=None,
        funcProgress=None,
        jobWorkQueue=None,
        controlQueue=None,
        log=None,
    ):
        super(JobQueue, self).__init__(parent)

        self.__log = None
        self.__progress = None
        self.__model = None
        self.__proxyModel = None

        self.parent = parent
        self.proxyModel = proxyModel
        self.progress = funcProgress
        self.controlQueue = controlQueue

        if jobWorkQueue is None:
            self._workQueue = deque()
        else:
            self._workQueue = jobWorkQueue

        self.log = log
        self.runJobs = RunJobs(
            self, self, controlQueue=self.controlQueue, log=self.log
        )  # progress function is a late bind
        self.statusUpdateSignal.connect(self.statusUpdate)
        self.runSignal.connect(self.run)
        jobID = config.data.get("JobID")

        if jobID:
            if jobID > 9999:
                # Roll over
                jobID = 1

            self.__jobID = jobID

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
        return self.__model

    @property
    def proxyModel(self):
        return self.__proxyModel

    @proxyModel.setter
    def proxyModel(self, value):
        if isinstance(value, TableProxyModel):
            self.__proxyModel = value
            self.__model = value.sourceModel()

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    @Slot(object, str)
    def statusUpdate(self, job, status):

        self.model.setData(job.statusIndex, status)

    def append(self, jobRow):
        """
        append append job to queue

        Args:
            jobRow (QModelIndex): index for job status on dataset
            oCommand (list): job row on dataset

        Returns:
            bool: True if append successful False otherwise
        """

        # job = self.model.dataset[
        #    jobRow,
        # ]

        status = self.model.dataset[jobRow,][JobKey.Status]
        if status != JobStatus.AddToQueue:
            if status == JobStatus.Waiting:
                self.addWaitingItemSignal.emit()
            return False

        jobID = self.model.dataset[jobRow,][JobKey.ID]
        #jobIndex = self.model.index(jobRow, JobKey.ID)
        #statusIndex = self.model.index(jobRow, JobKey.Status)
        #commandIndex = self.model.index(jobRow, JobKey.Command)
        jobIndex = FakeModelIndex(jobRow, JobKey.ID)
        statusIndex = FakeModelIndex(jobRow, JobKey.Status)
        commandIndex = FakeModelIndex(jobRow, JobKey.Command)

        if not jobID:
            self.model.setData(jobIndex, self.__jobID)
            self.__jobID += 1
            config.data.set(config.ConfigKey.JobID, self.__jobID)

        newJob = JobInfo(
            [jobIndex, statusIndex, commandIndex],
            self.model.dataset[jobRow,],
            self.model,
            log=self.log,
        )
        self._workQueue.append(newJob)
        self.model.setData(statusIndex, JobStatus.Queue)

        if self._workQueue:
            self.addQueueItemSignal.emit()
            return True

        return False

    def clear(self):
        """Clear the job queue"""

        while job := self.pop():
            print("Clearing the way {}".format(job.job[JobKey.ID]))

    def popLeft(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            element = self._workQueue.popleft()
            self._checkEmptied()

            return element

        return None

    def popRight(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            element = self._workQueue.pop()
            self._checkEmptied()

            return element

        return None

    def pop(self):
        """
        pop return next job in queue

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            element = self._workQueue.popleft()
            self._checkEmptied()

            return element

        return None

    def _checkEmptied(self):

        if not self._workQueue:
            self.queueEmptiedSignal.emit()

    @Slot()
    def run(self):
        """
        run test run worker thread
        """

        self.runJobs.proxyModel = self.proxyModel
        self.runJobs.progress = self.progress
        self.runJobs.output = self.output
        self.runJobs.log = self.log

        if JobQueue.__firstRun:
            self.parent.jobsOutput.setCurrentIndexSignal.emit()
            JobQueue.__firstRun = False

        self.runJobs.run()