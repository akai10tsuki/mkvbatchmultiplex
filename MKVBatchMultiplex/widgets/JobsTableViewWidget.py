"""
JobsTableWidget
"""

import logging

from PySide2.QtCore import QThreadPool, Qt, Slot

from PySide2.QtWidgets import QWidget, QGroupBox, QGridLayout, QApplication

from vsutillib.pyqt import QPushButtonWidget, darkPalette
from vsutillib.process import isThreadRunning

from .. import config
from ..jobs import JobStatus, RunJobs
from ..delegates import StatusComboBoxDelegate
from ..utils import populate, Text

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

    def __init__(self, parent, proxyModel, title=None):
        super(JobsTableViewWidget, self).__init__(parent)

        self.__output = None

        self.parent = parent
        self.proxyModel = proxyModel
        self.tableModel = proxyModel.sourceModel()

        self.tableView = JobsTableView(self, proxyModel, title)
        self.threadpool = QThreadPool()
        self.delegates = {}

        self._initUI(title)
        self._setupDelegates()
        self._initHelper()

    def _initUI(self, title):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(title)

        btnPopulate = QPushButtonWidget(
            "Populate",
            function=lambda: populate(self.tableModel),
            toolTip="Add test jobs to table",
        )

        btnAddWaitingJobsToQueue = QPushButtonWidget(
            "Queue Waiting Jobs",
            function=self.addWaitingJobsToQueue,
            toolTip="Add all Waiting jobs to the queue",
        )

        btnClearJobsQueue = QPushButtonWidget(
            "Clear Queue",
            function=self.clearJobsQueue,
            toolTip="Remove Jobs from Queue",
        )

        btnRun = QPushButtonWidget(
            "Start Queue", function=self.run, toolTip="Start processing jobs on Queue"
        )

        btnPrintDataset = QPushButtonWidget(
            "Debug",
            function=self.printDataset,
            toolTip="Print current dataset to console",
        )

        self.grpGrid.addWidget(self.tableView, 0, 0, 1, 5)
        self.grpGrid.addWidget(btnPopulate, 1, 0)
        self.grpGrid.addWidget(btnAddWaitingJobsToQueue, 1, 1)
        self.grpGrid.addWidget(btnClearJobsQueue, 1, 2)
        self.grpGrid.addWidget(btnRun, 1, 3)
        self.grpGrid.addWidget(btnPrintDataset, 1, 4)

        self.grpBox.setLayout(self.grpGrid)

        grid.addWidget(self.grpBox)

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

    def _initHelper(self):

        # Job Queue related
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobRunQueueState(True)
        )

        self.parent.jobsQueue.runJobs.startSignal.connect(lambda: self.jobStatus(True))
        self.parent.jobsQueue.runJobs.finishedSignal.connect(lambda: self.jobStatus(False))

        self.grpGrid.itemAt(config.JTVBTNRUN).widget().setEnabled(False)

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

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

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
        if self.parent.jobsQueue:
            print(
                "Something to Clear Total Jobs = {}".format(len(self.parent.jobsQueue))
            )
        else:
            print("Nothing here")

    def setLanguage(self):
        """
        setLanguage set labels according to locale
        """

        for index in range(self.grpGrid.count()):
            widget = self.grpGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText(_(widget.originalText))
                widget.setStatusTip(_(widget.toolTip))

        self.grpBox.setTitle(_(Text.txt0130))
        self.tableModel.setHeaderData(JOBSTATUS, Qt.Horizontal, _(Text.txt0131))
        self.tableModel.setHeaderData(JOBCOMMAND, Qt.Horizontal, _(Text.txt0132))

    def printDataset(self):
        """
        printDataset development debug
        """

        QApplication.setPalette(darkPalette())

        dataset = self.tableModel.dataset
        for r in range(0, len(dataset)):
            self.parent.outputMainSignal.emit(
                "Row {} ID {} Status {}\n".format(r, dataset[r, 0], dataset[r, 1]), {}
            )
            # print("Row {} ID {} Status {}".format(r, dataset[r, 0], dataset[r, 1]))

        self.parent.outputMainSignal.emit("\n", {})
        # self.parent.outputMainSignal.emit("The Color Red\n", {"color": Qt.red})
        # print()

    @Slot(bool)
    def jobRunQueueState(self, state):

        if state and not isThreadRunning(config.WORKERTHREADNAME):
            self.grpGrid.itemAt(config.JTVBTNRUN).widget().setEnabled(state)
        else:
            self.grpGrid.itemAt(config.JTVBTNRUN).widget().setEnabled(state)

    @Slot(bool)
    def jobStatus(self, running):
        if running:
            self.jobRunQueueState(False)
            print('running signal jobStatus CommandWidget')
        else:
            print('ended signal jobStatus CommandWidget')

    def run(self):
        """
        run test run worker thread
        """

        # self.runJobs = RunJobs(self, self.parent.jobsQueue, self.parent.progress)
        # self.runJobs.run()
        self.parent.jobsQueue.run()
