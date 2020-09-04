"""
JobsTableWidget
"""

import logging

try:
    import cPickle as pickle
except:
    import pickle
import zlib


from PySide2.QtCore import QThreadPool, Qt, Slot
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QApplication,
)

from vsutillib.pyqt import QPushButtonWidget, darkPalette, TabWidgetExtension
from vsutillib.process import isThreadRunning

from .. import config
from ..jobs import JobStatus, JobKey, SqlJobsTable, JobsTableKey
from ..delegates import StatusComboBoxDelegate
from ..utils import populate, Text, yesNoDialog

from .JobsTableView import JobsTableView

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsTableViewWidget(TabWidgetExtension, QWidget):
    """
    JobsTableViewWidget [summary]

    Args:
        JobsTableView ([type]): [description]
        QWidget ([type]): [description]
    """

    # Class logging state
    __log = False

    def __init__(self, parent, proxyModel, controlQueue, title=None, log=None):
        super(JobsTableViewWidget, self).__init__(parent=parent, tabWidgetChild=self)

        self.__output = None
        self.__log = None
        self.__tab = None

        self.parent = parent
        self.proxyModel = proxyModel
        self.model = proxyModel.sourceModel()
        self.controlQueue = controlQueue
        self.tableView = JobsTableView(self, proxyModel, title)
        self.delegates = {}

        self._initUI(title)
        self._setupDelegates()
        self._initHelper()

        self.log = log

    def _initUI(self, title):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(title)

        if config.data.get(config.ConfigKey.SimulateRun):
            btnPopulate = QPushButtonWidget(
                Text.txt0120,
                function=lambda: populate(self.model),
                toolTip=Text.txt0121,
            )

        btnAddWaitingJobsToQueue = QPushButtonWidget(
            Text.txt0122, function=self.addWaitingJobsToQueue, toolTip=Text.txt0123,
        )
        btnClearJobsQueue = QPushButtonWidget(
            Text.txt0124, function=self.clearJobsQueue, toolTip=Text.txt0125,
        )
        btnStartQueue = QPushButtonWidget(
            Text.txt0126, function=self.parent.jobsQueue.run, toolTip=Text.txt0127,
        )
        btnPrintDataset = QPushButtonWidget(
            Text.txt0128, function=self.printDataset, toolTip=Text.txt0129,
        )
        btnAbortCurrentJob = QPushButtonWidget(
            Text.txt0134, function=self.abortCurrentJob, toolTip=Text.txt0135,
        )
        btnAbortJobs = QPushButtonWidget(
            Text.txt0136, function=self.abortCurrentJob, toolTip=Text.txt0137,
        )

        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnAddWaitingJobsToQueue)
        self.btnGrid.addWidget(btnClearJobsQueue)
        self.btnGrid.addWidget(btnStartQueue)
        self.btnGrid.addWidget(btnAbortCurrentJob)
        self.btnGrid.addWidget(btnAbortJobs)
        self.btnGrid.addStretch()
        if config.data.get(config.ConfigKey.SimulateRun):
            self.btnGrid.addWidget(btnPopulate)
            self.btnGrid.addWidget(btnPrintDataset)

        self.btnGroup = QGroupBox("")
        self.btnGroup.setLayout(self.btnGrid)

        self.grpGrid.addWidget(self.tableView, 0, 0, 1, 5)
        self.grpGrid.addWidget(self.btnGroup, 1, 0, 1, 5)

        self.grpBox.setLayout(self.grpGrid)

        grid.addWidget(self.grpBox)
        self.setLayout(grid)

    def _setupDelegates(self):
        """
        Store delegates in self.delegates dictionary by column name and apply
        delegates to table view
        """

        self.delegates["status"] = StatusComboBoxDelegate(self.proxyModel)

        for columnName, delegate in self.delegates.items():
            for i, column in enumerate(self.model.dataset.headerName):
                if column == columnName:
                    self.tableView.setItemDelegateForColumn(i, delegate)

    def _initHelper(self):

        # Job Queue related
        self.parent.jobsQueue.statusChangeSignal.connect(self.jobAddWaitingState)
        self.parent.jobsQueue.statusChangeSignal.connect(self.jobStatusChangeCheck)
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobStartQueueState(True)
        )
        self.parent.jobsQueue.addQueueItemSignal.connect(
            lambda: self.jobClearQueueState(True)
        )
        self.parent.jobsQueue.queueEmptiedSignal.connect(
            lambda: self.jobClearQueueState(False)
        )
        self.parent.jobsQueue.queueEmptiedSignal.connect(
            lambda: self.jobStartQueueState(False)
        )

        # Job Queue Worker start/End
        self.parent.jobsQueue.runJobs.startSignal.connect(lambda: self.jobStatus(True))
        self.parent.jobsQueue.runJobs.finishedSignal.connect(
            lambda: self.jobStatus(False)
        )

        # Default button state
        self.btnGrid.itemAt(_Button.ADDWAITING).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.CLEARQUEUE).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.ABORTCURRENTJOB).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.ABORTJOBS).widget().setEnabled(False)

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

    @property
    def tab(self):
        return self.__tab

    @tab.setter
    def tab(self, value):
        self.__tab = value

    @property
    def tabWidget(self):
        return self.__tabWidget

    @tabWidget.setter
    def tabWidget(self, value):
        self.__tabWidget = value

    def abortCurrentJob(self):
        self.controlQueue.append(JobStatus.AbortJob)

    def abortJobs(self):
        self.controlQueue.append(JobStatus.Abort)

    def addWaitingJobsToQueue(self):
        """
        addWaitingJobsToQueue adds any Waiting job to job queue
        """

        for row in range(self.model.rowCount()):
            rowStatus = self.model.dataset[row, 1]

            if rowStatus == JobStatus.Waiting:
                index = self.model.index(row, 1)
                self.model.setData(index, JobStatus.AddToQueue)

        # self.jobAddWaitingState()

    def clearJobsQueue(self):
        """
        clearJobsQueue delete any remaining jobs from Queue
        """

        if len(self.parent.jobsQueue) > 0:
            language = config.data.get(config.ConfigKey.Language)
            bAnswer = False
            title = _(Text.txt0124)
            msg = "¿" if language == "es" else ""
            msg += _(Text.txt0125) + "?"
            bAnswer = yesNoDialog(self, msg, title)

            if bAnswer:
                while job := self.parent.jobsQueue.pop():

                    self.model.setData(job.statusIndex, JobStatus.Waiting)
            # else:
            #    print("Nothing here")

    def setLanguage(self):
        """
        setLanguage set labels according to locale
        """

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setToolTip(_(widget.toolTip))

        self.grpBox.setTitle(_(Text.txt0130))
        self.model.setHeaderData(
            JobKey.ID, Qt.Horizontal, "  " + _(Text.txt0131) + "  "
        )
        self.model.setHeaderData(
            JobKey.Status, Qt.Horizontal, "  " + _(Text.txt0132) + "  "
        )
        self.model.setHeaderData(JobKey.Command, Qt.Horizontal, _(Text.txt0133))

    def printDataset(self):
        """
        printDataset development debug
        """

        QApplication.setPalette(darkPalette())
        dataset = self.model.dataset

        for r in range(0, len(dataset)):
            self.output.command.emit(
                "Row {} ID {} Status {}\n".format(
                    r, dataset[r, JobKey.ID], dataset[r, JobKey.Status]
                ),
                {},
            )

        self.output.command.emit("\n", {})

    @Slot(object)
    def jobAddWaitingState(self):

        self.btnGrid.itemAt(_Button.ADDWAITING).widget().setEnabled(
            hasWaiting(self.model)
        )

    @Slot(bool)
    def jobClearQueueState(self, state):

        self.btnGrid.itemAt(_Button.CLEARQUEUE).widget().setEnabled(state)

    @Slot(bool)
    def jobStartQueueState(self, state):

        if state and not isThreadRunning(config.WORKERTHREADNAME):
            self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.STARTQUEUE).widget().setEnabled(False)

    @Slot(bool)
    def jobStatus(self, running):

        if running:
            self.jobStartQueueState(False)

        self.btnGrid.itemAt(_Button.ABORTCURRENTJOB).widget().setEnabled(running)
        self.btnGrid.itemAt(_Button.ABORTJOBS).widget().setEnabled(running)

    @Slot(object)
    def jobStatusChangeCheck(self, index):

        row = index.row()
        column = index.column()

        rowStatus = self.model.dataset[row, column]

        if rowStatus == JobStatus.Abort:
            self.controlQueue.append(JobStatus.AbortJob)


def hasWaiting(model):
    """
    hasWaiting looks for a Waiting status

    Args:
        model (TableModel): a table model

    Returns:
        bool: True if Waiting status found. False otherwise.
    """

    for r in range(0, len(model.dataset)):
        if model.dataset[r, JobKey.Status] == JobStatus.Waiting:
            return True

    return False


class _Button:

    ADDWAITING = 0
    CLEARQUEUE = 1
    STARTQUEUE = 2
    ABORTCURRENTJOB = 3
    ABORTJOBS = 4
    FETCHJOBHISTORY = 6
