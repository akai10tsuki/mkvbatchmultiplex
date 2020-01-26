"""
JobsTableWidget
"""

import logging
import time

from PySide2.QtCore import QThreadPool, Slot
from PySide2.QtWidgets import QWidget, QGroupBox, QGridLayout, QPushButton

from vsutillib.pyqt import QthThreadWorker

from ..jobs import JobStatus
from ..delegates import StatusComboBoxDelegate

from .JobsTableView import JobsTableView

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())
JOBID, JOBSTATUS, JOBCOMMAND = range(3)


class JobsTableViewWidget(QWidget):
    """
    JobsTableViewWidget [summary]

    Args:
        JobsTableView ([type]): [description]
        QWidget ([type]): [description]
    """

    # Class logging state
    __log = False

    def __init__(self, parent=None, proxyModel=None, jobQueue=None, title=None):

        super(JobsTableViewWidget, self).__init__(parent)

        self.parent = parent
        self.proxyModel = proxyModel
        self.tableModel = proxyModel.sourceModel()
        self.jobsQueue = jobQueue

        self.tableView = JobsTableView(self, proxyModel, title)
        self.threadpool = QThreadPool()
        self.delegates = {}

        self._initUI(title)
        self._setupDelegates()

    def _initUI(self, title):

        grid = QGridLayout()
        grpGrid = QGridLayout()
        grpBox = QGroupBox(title)

        btnAddWaitingJobsToQueue = QPushButton(" Queue Waiting Jobs ")
        btnAddWaitingJobsToQueue.resize(btnAddWaitingJobsToQueue.sizeHint())
        btnAddWaitingJobsToQueue.clicked.connect(self.addWaitingJobsToQueue)
        btnAddWaitingJobsToQueue.setToolTip("Add all Waiting jobs to the queue.")

        btnClearJobsQueue = QPushButton(" Clear Queue ")
        btnClearJobsQueue.resize(btnClearJobsQueue.sizeHint())
        btnClearJobsQueue.clicked.connect(self.clearJobsQueue)
        btnClearJobsQueue.setToolTip("Remove Jobs from Queue.")

        btnRun = QPushButton(" Simulate Run ")
        btnRun.resize(btnRun.sizeHint())
        btnRun.clicked.connect(self.run)
        btnRun.setToolTip("Clear Queue simulating a run")

        btnPrintDataset = QPushButton(" Debug ")
        btnPrintDataset.resize(btnClearJobsQueue.sizeHint())
        btnPrintDataset.clicked.connect(self.printDataset)
        btnPrintDataset.setToolTip("Print current dataset to console")

        grpGrid.addWidget(self.tableView, 0, 0, 1, 4)
        grpGrid.addWidget(btnAddWaitingJobsToQueue, 1, 0)
        grpGrid.addWidget(btnClearJobsQueue, 1, 1)
        grpGrid.addWidget(btnRun, 1, 2)
        grpGrid.addWidget(btnPrintDataset, 1, 3)

        grpBox.setLayout(grpGrid)

        grid.addWidget(grpBox)

        self.setLayout(grid)

    def _setupDelegates(self):
        """
        Store delegates in self.delegates dictionary by column name and apply delegates to table
        view
        """

        self.delegates["status"] = StatusComboBoxDelegate(self.proxyModel)

        for columnName, delegate in self.delegates.items():

            for i, column in enumerate(self.tableModel.dataset.headerName):

                if column == columnName:
                    self.tableView.setItemDelegateForColumn(i, delegate)

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

        return JobsTableView.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def addWaitingJobsToQueue(self):
        """
        addWaitingJobsToQueue adds any Waiting job to job queue
        """

        for row in range(self.tableModel.rowCount()):
            rowStatus = self.tableModel.dataset[row, 1]

            if rowStatus == JobStatus.Waiting:
                index = self.tableModel.index(row, 1)
                self.tableModel.setData(index, JobStatus.AddToQueue)

    def clearJobsQueue(self):

        if self.jobsQueue:
            print("Something to Clear Total Jobs = {}".format(len(self.jobsQueue)))
        else:
            print("Nothing here")

    def printDataset(self):

        dataset = self.tableModel.dataset

        for r in range(0, len(dataset)):
            print("Row {} ID {} Status {}".format(r, dataset[r, 0], dataset[r, 1]))

        print()

    def run(self):

        if self.jobsQueue:
            jobToRun = QthThreadWorker(
                runJobs, self.tableModel, self.jobsQueue, funcResult=result
            )

            self.threadpool.start(jobToRun)

        else:

            print("No work to be done...")


def result(funcResult):

    print(funcResult)


def progress(job):

    print("progress")


def runJobs(jobQueue, funcProgress=None):
    """
    runJobs execute jobs on queue

    Args:
        jobQueue (JobQueue): Job queue has all related information for the job
        funcProgress (func, optional): function to call to report job progress. Defaults to None.

    Returns:
        str: Dummy  return value
    """

    while job := jobQueue.popLeft():

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Running)

        print(
            "({}, {}) {} Running.. ".format(
                job.statusIndex.row(), job.statusIndex.column(), job.job[JOBID],
            )
        )

        time.sleep(10)

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Done)

    return "Job queue empty."