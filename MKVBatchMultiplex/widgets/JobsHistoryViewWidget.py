"""
JobsHistoryViewWidget
"""

import copy
import logging

try:
    import cPickle as pickle
except:
    import pickle
import re
import zlib

from datetime import datetime
from pprint import pprint
from time import sleep

from PySide2.QtCore import QThreadPool, Qt, Slot
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QApplication,
)

from vsutillib.pyqt import (
    darkPalette,
    QPushButtonWidget,
    QOutputTextWidget,
    SvgColor,
    TabWidgetExtension,
)
from vsutillib.process import isThreadRunning
from vsutillib.mkv import MKVParseKey

from .. import config
from ..jobs import (
    JobHistoryKey,
    JobStatus,
    JobKey,
    SqlJobsTable,
    JobsTableKey,
    JobQueue,
)
from ..dataset import TableData, tableHeaders, tableHistoryHeaders
from ..delegates import StatusComboBoxDelegate
from ..models import TableModel, TableProxyModel, JobsTableModel
from ..utils import populate, Text, yesNoDialog

from .JobsHistoryView import JobsHistoryView

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsHistoryViewWidget(TabWidgetExtension, QWidget):
    """
    JobsHistoryViewWidget [summary]

    Args:
        JobsHistoryView ([type]): [description]
        QWidget ([type]): [description]
    """

    def __init__(self, parent, title=None, log=None):
        super().__init__(parent=parent, tabWidgetChild=self)

        self.__output = None
        self.__log = None
        self.__tab = None
        self.__originalTab = None

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

        self.output = QOutputTextWidget(self)

        btnFetchJobHistory = QPushButtonWidget(
            "Fetch History",
            function=self.fetchJobHistory,
            toolTip="Fetch and display old saved jobs processed by worker",
        )
        btnClearSelection = QPushButtonWidget(
            "Clear Selection",
            function=self.tableView.clearSelection,
            toolTip="Clear selected rows",
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
        btnSelectAll = QPushButtonWidget(
            "Select All", function=self.tableView.selectAll, toolTip="Select all rows"
        )
        btnShowOutput = QPushButtonWidget(
            "Show Output", function=self.showOutput, toolTip="Show job output run"
        )
        btnShowOutputErrors = QPushButtonWidget(
            "Show Errors",
            function=self.showOutputErrors,
            toolTip="Show job output errors",
        )

        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnFetchJobHistory)
        self.btnGrid.addWidget(btnShowOutput)
        self.btnGrid.addWidget(btnShowOutputErrors)
        self.btnGrid.addStretch()
        self.btnGrid.addWidget(btnSelectAll)
        self.btnGrid.addWidget(btnClearSelection)
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

    @Slot()
    def setLanguage(self):
        """
        setLanguage set labels according to locale
        """

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setText("  " + _(widget.originalText) + "  ")
                widget.setToolTip(_(widget.toolTip))

        # self.grpBox.setTitle(_(Text.txt0130))
        # self.model.setHeaderData(
        #    JobKey.ID, Qt.Horizontal, "  " + _(Text.txt0131) + "  "
        # )
        # self.model.setHeaderData(
        #    JobKey.Status, Qt.Horizontal, "  " + _(Text.txt0132) + "  "
        # )
        # self.model.setHeaderData(JobKey.Command, Qt.Horizontal, _(Text.txt0133))

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

        # self.model.dataset.data.clear()

        while self.model.rowCount() > 0:
            element = self.model.removeRow(0)

        jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            rowNumber = 0
            if rows:
                for row in rows:
                    viewRow = [None, None, None, None]
                    job = pickle.loads(zlib.decompress(row[JobsTableKey.jobIndex]))
                    dt = datetime.fromtimestamp(job.startTime)
                    viewRow[JobHistoryKey.ID] = [
                        row[JobsTableKey.IDIndex],
                        "",
                        row[JobsTableKey.rowidIndex],
                    ]
                    viewRow[JobHistoryKey.Date] = [
                        dt.isoformat(sep=" "),
                        "Date job was executed",
                        None,
                    ]
                    viewRow[JobHistoryKey.Status] = [
                        job.jobRow[JobKey.Status],
                        "",
                        None,
                    ]
                    viewRow[JobHistoryKey.Command] = [
                        job.jobRow[JobKey.Command],
                        job.jobRow[JobKey.Command],
                        None,
                    ]
                    self.model.insertRows(rowNumber, 1, data=viewRow)
                    rowNumber += 1

            # jobOutputRun = self.model.dataset.data[0][JobHistoryKey.Command].obj

        jobsDB.close()

    def showOutput(self):

        indexes = self.tableView.selectionModel().selectedRows()

        if len(indexes) == 1:
            self.parent.progressSpin.startAnimationSignal.emit()
            sleep(1)
            jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))

            index = self.proxyModel.mapToSource(indexes[0])
            row = index.row()
            column = index.column()
            jobID = self.model.dataset.data[row][column].cell
            job = self.model.dataset.data[row][JobHistoryKey.Command].obj
            rowid = self.model.dataset.data[row][JobHistoryKey.ID].obj
            if job is None:
                records = jobsDB.fetchJob({"rowid": rowid}, JobsTableKey.job)
                if records:
                    record = records.fetchone()
                    job = pickle.loads(zlib.decompress(record[1]))
                    self.model.dataset.data[row][
                        JobHistoryKey.Command
                    ].obj = copy.deepcopy(job)
                    print("Job Fetched {}".format(job.jobRow[JobKey.ID]))
                else:
                    msg = "Information cannot be read."
                    self.output.insertTextSignal.emit(msg, {})
                    return

            regPercentEx = re.compile(r":\W*(\d+)%$")
            # The file 'file name' has been opened for writing.
            regOutputFileEx = re.compile(r"file (.*?) has")
            indexes = self.tableView.selectedIndexes()

            self.output.clear()
            processedFiles = 0
            totalFiles = len(job.oCommand)
            for line in job.output:
                if m := regPercentEx.search(line):
                    n = int(m.group(1))
                    if n < 100:
                        continue
                if f := regOutputFileEx.search(line):
                    processedFiles += 1
                self.output.insertTextSignal.emit(line, {})
            msg = stats(job)

            self.output.insertTextSignal.emit(msg, {})
            self.parent.progressSpin.stopAnimationSignal.emit()

    def showOutputErrors(self):

        indexes = self.tableView.selectedIndexes()
        if indexes:
            self.output.clear()
            index = indexes[0]
            sourceIndex = self.proxyModel.mapToSource(index)
            row = sourceIndex.row()
            column = sourceIndex.column()
            jobID = self.model.dataset.data[row][column].cell
            job = self.model.dataset.data[row][JobHistoryKey.Command].obj

            for analysis in job.errors:

                msg = "Error Job ID: {} ---------------------\n\n".format(
                    job.jobRow[JobKey.ID]
                )

                self.output.insertTextSignal.emit(
                    msg, {"color": SvgColor.red, "appendEnd": True}
                )

                # msg = "\nDestination File: {}\n\n".format(destinationFile)
                # output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})

                for i, m in enumerate(analysis):
                    if i == 0:
                        lines = m.split("\n")
                        findSource = True
                        for index, line in enumerate(lines):
                            color = SvgColor.orange
                            if findSource and (
                                (searchIndex := line.find("File Name")) >= 0
                            ):
                                if searchIndex >= 0:
                                    color = SvgColor.tomato
                                    findSource = False
                            self.output.insertTextSignal.emit(
                                line + "\n", {"color": color}
                            )
                    else:
                        self.output.insertTextSignal.emit(m, {"color": SvgColor.red})

                msg = "Error Job ID: {} ---------------------\n\n".format(
                    job.jobRow[JobKey.ID]
                )
                self.output.insertTextSignal.emit(
                    msg, {"color": SvgColor.red, "appendEnd": True}
                )

    def refresh(self):

        jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            for row in rows:
                job = pickle.loads(zlib.decompress(row[JobsTableKey.jobIndex]))
                print(
                    "Job ID = {} Status = {}".format(
                        row[JobsTableKey.IDIndex], job.jobRow[JobKey.Status]
                    )
                )

        jobsDB.close()


def stats(job):

    totalFiles = len(job.oCommand)
    totalErrors = len(job.errors)
    processedFiles = totalFiles - totalErrors

    dtStart = datetime.fromtimestamp(job.startTime)
    dtStartSuffix = ""
    if job.endTime is not None:
        dtEnd = datetime.fromtimestamp(job.endTime)
        dtDuration = dtEnd - dtStart
    else:
        dtStartSuffix += " - Did not end execution"
        processedFiles = "undetermined"
        dtDuration = 0

    # msg = "\nJob ID = {}\n\nProcessed: {}\nProcessed time: {}\nTotal Files: {} proccessed file {} Errors {}".format(
    #    jobID, dtStart.isoformat(), dtDuration, totalFiles, processedFiles, totalFiles - processedFiles
    # )

    msg = """

    Job ID = {}

    Processed: {}
    Processed time: {}

    Total files: {}
    Proccessed files: {}
    Errors {}

    """

    msg = msg.format(
        job.jobRow[JobKey.ID],
        dtStart.isoformat() + dtStartSuffix,
        dtDuration,
        totalFiles,
        processedFiles,
        totalErrors,
    )

    return msg


class _Button:

    FETCHJOBHISTORY = 0
