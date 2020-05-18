"""
JobsHistoryViewWidget
"""

import logging

try:
    import cPickle as pickle
except:
    import pickle
import zlib

from datetime import datetime
from pprint import pprint

from PySide2.QtCore import QThreadPool, Qt, Slot
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QApplication,
)

from vsutillib.pyqt import QPushButtonWidget, darkPalette, OutputTextWidget
from vsutillib.process import isThreadRunning

from .. import config
from ..jobs import JobHistoryKey, JobStatus, JobKey, SqlJobsDB, JobsDBKey, JobQueue
from ..dataset import TableData, tableHeaders, tableHistoryHeaders
from ..delegates import StatusComboBoxDelegate
from ..models import TableModel, TableProxyModel, JobsTableModel
from ..utils import populate, Text, yesNoDialog

from .JobsHistoryView import JobsHistoryView

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsHistoryViewWidget(QWidget):
    """
    JobsHistoryViewWidget [summary]

    Args:
        JobsHistoryView ([type]): [description]
        QWidget ([type]): [description]
    """

    def __init__(self, parent, title=None, log=None):
        super(JobsHistoryViewWidget, self).__init__(parent)

        self.__output = None
        self.__log = None
        self.__tab = None

        queue = JobQueue

        self.parent = parent
        headers = tableHistoryHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = TableModel(self.tableData)
        self.proxyModel = TableProxyModel(self.model)
        self.tableView = JobsHistoryView(self, self.proxyModel, title)

        self._initUI(title)
        self._initHelper()

        self.log = log

    def _initUI(self, title):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(title)

        self.output = OutputTextWidget(self)

        btnFetchJobHistory = QPushButtonWidget(
            "Fetch History",
            function=self.fetchJobHistory,
            toolTip="Fetch and display old saved jobs processed by worker",
        )
        btnClearOutput = QPushButtonWidget(
            "Clear Output",
            function=self.clearOutputWindow,
            toolTip="Clear output window",
        )
        btnRefresh = QPushButtonWidget(
            "Refresh",
            function=self.refresh,
            toolTip="Refresh table view with any new information",
        )

        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnFetchJobHistory)
        self.btnGrid.addStretch()
        self.btnGrid.addWidget(btnClearOutput)

        self.btnGroup = QGroupBox("")
        self.btnGroup.setLayout(self.btnGrid)

        self.grpGrid.addWidget(self.tableView, 0, 0, 1, 5)
        self.grpGrid.addWidget(self.output, 1, 0, 1, 5)
        self.grpGrid.addWidget(self.btnGroup, 2, 0, 1, 5)

        self.grpBox.setLayout(self.grpGrid)

        grid.addWidget(self.grpBox)
        self.setLayout(grid)

    def _initHelper(self):

        self.btnGrid.itemAt(_Button.FETCHJOBHISTORY).widget().setEnabled(True)

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

    def clearOutputWindow(self):
        """
        clearOutputWindow clear the command output window
        """

        self.output.clear()

        # [
        #    [1, "", None],
        #    [job.AddToQueue, "", None],
        #    [job.oCommand.strCommand, job.oCommand.strCommand, None],
        # ]

    def fetchJobHistory(self):
        jobsDB = SqlJobsDB(config.data.get(config.ConfigKey.JobsDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            rowNumber = 0
            for row in rows:
                viewRow = [None, None, None, None]
                job = pickle.loads(zlib.decompress(row[JobsDBKey.jobIndex]))
                dt = datetime.fromtimestamp(job.startTime)
                viewRow[JobHistoryKey.ID] = [row[JobsDBKey.IDIndex], "", None]
                viewRow[JobHistoryKey.Date] = [
                    dt.isoformat(),
                    "Date job was executed",
                    None,
                ]
                viewRow[JobHistoryKey.Status] = [job.jobRow[JobKey.Status], "", None]
                viewRow[JobHistoryKey.Command] = [
                    job.jobRow[JobKey.Command],
                    job.jobRow[JobKey.Command],
                    job.output,
                ]
                self.model.insertRows(rowNumber, 1, data=viewRow)
                rowNumber += 1

            # jobOutputRun = self.model.dataset.data[0][JobHistoryKey.Command].obj

        jobsDB.close()

    def refresh(self):

        jobsDB = SqlJobsDB(config.data.get(config.ConfigKey.JobsDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            for row in rows:
                job = pickle.loads(zlib.decompress(row[JobsDBKey.jobIndex]))
                print(
                    "Job ID = {} Status = {}".format(
                        row[JobsDBKey.IDIndex], job.jobRow[JobKey.Status]
                    )
                )

        jobsDB.close()


class _Button:

    FETCHJOBHISTORY = 0
