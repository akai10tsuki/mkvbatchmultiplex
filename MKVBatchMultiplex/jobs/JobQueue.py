"""
 Jobs class to manage jobs queue
"""
# JOB0001

import copy
import logging

from collections import deque
from datetime import datetime
from time import time

from PySide2.QtCore import QObject, Slot, Signal


from vsutillib.mkv import MKVCommandParser

from .. import config
from ..models import TableProxyModel
from .JobKeys import JobStatus, JobKey
from .RunJobs import RunJobs


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobInfo:  # pylint: disable=too-many-instance-attributes
    """
    JobInfo Information for a job

    Args:
        **status** (str, optional): job status. Defaults to "".

        **index** (QModelIndex, optional): index on job in table. Defaults to None.

        **job** (list, optional): row on job in table. Defaults to None.

        **errors** (list, optional): errors on job execution. Defaults to None.

        **output** (list, optional): job execution output. Defaults to None.
    """

    def __init__(
        self, jobRowNumber, jobRow, tableModel, errors=None, output=None, log=False,
    ):

        self.__jobRow = []
        self.jobRowNumber = jobRowNumber
        self.jobRow = jobRow
        self.oCommand = copy.deepcopy(
            tableModel.dataset.data[jobRowNumber][JobKey.Command].obj
        )
        if (not self.oCommand) or (not self.oCommand.command):
            command = tableModel.dataset[jobRowNumber, JobKey.Command]
            self.oCommand = MKVCommandParser(command, log=log)
            if log:
                MODULELOG.debug(
                    "JBQ0001: Job %s- Bad MKVCommandParser object.", jobRow[JobKey.ID]
                )
        self.date = datetime.today()
        self.addTime = time()
        self.startTime = None
        self.endTime = None
        self.errors = [] if errors is None else errors
        self.output = [] if output is None else output

    @property
    def jobRow(self):
        """
        jobRow row of job in table read write

        Returns:
            int: row number of job in table
        """
        return self.__jobRow

    @jobRow.setter
    def jobRow(self, value):
        if isinstance(value, list):
            self.__jobRow = []
            for cell in value:
                self.__jobRow.append(cell)

    @property
    def status(self):
        """
        status of job read write

        Returns:
            [type]: [description]
        """
        return self.jobRow[JobKey.Status]

    @status.setter
    def status(self, value):
        if isinstance(value, str):
            self.jobRow[JobKey.Status] = value


class JobQueue(QObject):
    """
    JobQueue - class to manage jobs queue

    Args:
        **parent** (QWidget): parent widget

        **proxyModel** (TableProxyModel, optional): Proxy model for model/view.
        Defaults to None.

        **funcProgress** (function, optional): Function that updates progress bar.
        Defaults to None.

        **jobWorkQueue** (deque, optional): Queue to use to save Jobs to execute.
        Defaults to None.

        **controlQueue** (deque, optional): Queue to control Jobs execution.
        Some status conditions are routed through here to Stop, Skip or Abort Jobs.
        Defaults to None.

        **log** (bool, optional): Logging can be cotrolled using this parameter.
        Defaults to None.
    """

    # Class logging state
    __log = False

    __firstRun = True
    __jobID = 10

    statusUpdateSignal = Signal(object, str)
    runSignal = Signal()
    addQueueItemSignal = Signal(object)
    addWaitingItemSignal = Signal()
    queueEmptiedSignal = Signal()
    statusChangeSignal = Signal(object)

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

        return JobQueue.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @property
    def model(self):
        """
        model used in model/view read only

        Returns:
            JobsTableModel: model used in model/view
        """
        return self.__model

    @property
    def proxyModel(self):
        """
        proxyModel of model used in model/view read write

        Returns:
            TableProxyModel: Filtered model of source model used in model/view
        """
        return self.__proxyModel

    @proxyModel.setter
    def proxyModel(self, value):
        if isinstance(value, TableProxyModel):
            self.__proxyModel = value
            self.__model = value.sourceModel()

    @property
    def progress(self):
        """
        progress function to update progress bar read write

        Returns:
            DualProgressBar: progress bar of main window
        """
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    @Slot(object, str)
    def statusUpdate(self, job, status):
        """
        statusUpdate Slot to update status of a job

        Args:
            **job** (JobInfo): job to update

            **status** (str): new status to set
        """

        index = self.model.index(job.jobRowNumber, JobKey.Status)
        self.model.setData(index, status)

    def append(self, jobRow):
        """
        append job to Jobs queue

        Args:
            **jobRow** (QModelIndex): index for job status on dataset

        Returns:
            bool: True if append successful False otherwise
        """

        status = self.model.dataset[jobRow,][JobKey.Status]
        if status != JobStatus.AddToQueue:
            if status == JobStatus.Waiting:
                self.addWaitingItemSignal.emit()
            return False

        jobID = self.model.dataset[jobRow,][JobKey.ID]

        jobIndex = self.model.index(jobRow, JobKey.ID)

        if not jobID:
            self.model.setData(jobIndex, self.__jobID)
            self.__jobID += 1
            config.data.set(config.ConfigKey.JobID, self.__jobID)

        newJob = JobInfo(jobRow, self.model.dataset[jobRow,], self.model, log=self.log,)

        self._workQueue.append(newJob)
        index = self.model.index(jobRow, JobKey.Status)
        self.model.setData(index, JobStatus.Queue)
        if self._workQueue:
            index = self.model.index(jobRow, JobKey.ID)
            self.addQueueItemSignal.emit(index)
            return True

        return False

    def clear(self):
        """Clear the job queue"""

        while job := self.pop():
            print("Clearing the way {}".format(job.job[JobKey.ID]))

    def popLeft(self):
        """
        return next job in queue

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
        return last job in queue

        Returns:
            JobInfo: last job in queue
        """

        if self._workQueue:
            element = self._workQueue.pop()
            self._checkEmptied()

            return element

        return None

    def pop(self):
        """
        pop return next job in queue like popLeft

        Returns:
            JobInfo: next job in queue
        """

        if self._workQueue:
            element = self._workQueue.popleft()
            self._checkEmptied()

            return element

        return None

    def _checkEmptied(self):
        """
        _checkEmptied emit queueEmptiedSignal if job queue is empty
        """

        if not self._workQueue:
            self.queueEmptiedSignal.emit()

    @Slot()
    def run(self):
        """
        run will start the job queue
        """

        self.runJobs.proxyModel = self.proxyModel
        self.runJobs.progress = self.progress
        self.runJobs.output = self.output
        self.runJobs.log = self.log

        if JobQueue.__firstRun:
            self.parent.jobsOutputWidget.setAsCurrentTab()
            JobQueue.__firstRun = False

        self.runJobs.run()
