"""
JobsHistoryViewWidget
"""

import copy
import logging

try:
    import cPickle as pickle
except:  # pylint: disable=bare-except
    import pickle
import re
import zlib

from datetime import datetime, timedelta

# from pprint import pprint
from time import sleep

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
)

from vsutillib.pyqt import (
    QPushButtonWidget,
    QOutputTextWidget,
    qtRunFunctionInThread,
    SvgColor,
    TabWidgetExtension,
)

# from vsutillib.process import isThreadRunning
from vsutillib.misc import strFormatTimeDelta

# from vsutillib.mkv import MKVParseKey

from ..config import data as config
from ..config import ConfigKey

from ..jobs import (
    JobHistoryKey,
    JobKey,
    SqlJobsTable,
    JobsTableKey,
    JobQueue,
)
from ..dataset import TableData, tableHistoryHeaders

# from ..delegates import StatusComboBoxDelegate
from ..models import TableModel, TableProxyModel
from ..utils import Text, yesNoDialog

from .JobsHistoryView import JobsHistoryView
from .SearchTextDialogWidget import SearchTextDialogWidget

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsHistoryViewWidget(TabWidgetExtension, QWidget):
    """
    JobsHistoryViewWidget [summary]

    Args:
        JobsHistoryView ([type]): [description]
        QWidget ([type]): [description]
    """

    def __init__(self, parent=None, groupTitle=None, log=None):
        super().__init__(parent=parent, tabWidgetChild=self)

        self.__output = None
        self.__log = None
        self.__tab = None
        self.__originalTab = None

        self.parent = parent
        headers = tableHistoryHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = TableModel(self.tableData)
        self.proxyModel = TableProxyModel(self.model)
        self.tableView = JobsHistoryView(self, self.proxyModel, groupTitle)
        self.search = SearchTextDialogWidget(self)
        self._initUI(groupTitle)
        self._initHelper()

        self.log = log

    def _initUI(self, groupTitle):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(groupTitle)

        self.output = QOutputTextWidget(self)

        btnFetchJobHistory = QPushButtonWidget(
            "Fetch History",
            function=self.fetchJobHistory,
            toolTip="Fetch and display old saved jobs processed by worker",
        )
        btnSearchText = QPushButtonWidget(
            "Search",
            function=self.searchText,
            toolTip="Do full text search on commands",
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
        btnPrint = QPushButtonWidget(
            "Print", function=self.printDataset, toolTip="List Rows"
        )
        btnShowOutput = QPushButtonWidget(
            "Show Output",
            function=lambda: self.showOutput(_ShowKey.output),
            toolTip="Show job output run",
        )
        btnShowOutputErrors = QPushButtonWidget(
            "Show Errors",
            function=lambda: self.showOutput(_ShowKey.errors),
            toolTip="Show job output errors",
        )

        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnFetchJobHistory)
        self.btnGrid.addWidget(btnSearchText)
        self.btnGrid.addWidget(btnShowOutput)
        self.btnGrid.addWidget(btnShowOutputErrors)
        self.btnGrid.addStretch()
        self.btnGrid.addWidget(btnPrint)
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

    def fetchJobHistory(self):

        # while self.model.rowCount() > 0:
        #    element = self.model.removeRow(0)

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            if rows:
                totalRows = self.model.rowCount()
                if totalRows > 0:
                    self.model.removeRows(0, totalRows)
                fillRows(self, rows)

        jobsDB.close()

    def searchText(self):

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

        if jobsDB:
            rows = self.search.searchText(jobsDB)
            if rows:
                totalRows = self.model.rowCount()
                if totalRows > 0:
                    self.model.removeRows(0, totalRows)
                    # element = self.model.removeRow(0)
                fillRows(self, rows)

        jobsDB.close()

    def showOutput(self, outputType):

        qtRunFunctionInThread(
            showOutputLines,
            tableView=self.tableView,
            proxyModel=self.proxyModel,
            output=self.output,
            outputType=outputType,
            funcStart=self.parent.progressSpin.startAnimation,
            funcFinished=self.parent.progressSpin.stopAnimation,
        )

    # def listRows(self):

    def printDataset(self):
        """
        printDataset development debug
        """
        # QApplication.setPalette(darkPalette())
        dataset = self.model.dataset

        for r in range(0, len(dataset)):
            self.output.insertTextSignal.emit(
                "Row {} ID {} Status {}\n".format(
                    r, dataset[r, JobKey.ID], dataset[r, JobKey.Status]
                ),
                {},
            )

        self.output.insertTextSignal.emit("\n", {})

    def refresh(self):

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

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


def fillRows(self, rows):
    """
    fillRows fill view rows

    Args:
        rows (set): set with job information
    """

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
        dtStartSuffix += " - undetermined execution"
        processedFiles = "undetermined"
        dtDuration = timedelta()

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
        dtStart.isoformat(sep=" ") + dtStartSuffix,
        strFormatTimeDelta(dtDuration),
        totalFiles,
        processedFiles,
        totalErrors,
    )

    return msg


def showOutputLines(**kwargs):

    tableView = kwargs.pop(_ShowKey.tableView, None)
    proxyModel = kwargs.pop(_ShowKey.proxyModel, None)
    output = kwargs.pop(_ShowKey.output, None)
    outputType = kwargs.pop(_ShowKey.outputType, None)

    indexes = tableView.selectionModel().selectedRows()

    if len(indexes) == 1:
        output.clearSignal.emit()

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

        index = proxyModel.mapToSource(indexes[0])
        model = proxyModel.sourceModel()

        row = index.row()
        # column = index.column()
        job = model.dataset.data[row][JobHistoryKey.Command].obj
        rowid = model.dataset.data[row][JobHistoryKey.ID].obj
        if job is None:
            records = jobsDB.fetchJob({"rowid": rowid}, JobsTableKey.job)
            if records:
                record = records.fetchone()
                job = pickle.loads(zlib.decompress(record[1]))
                model.dataset.data[row][JobHistoryKey.Command].obj = copy.deepcopy(job)
            else:
                msg = "Information cannot be read."
                output.insertTextSignal.emit(msg, {"log": False})
                return

        if outputType == _ShowKey.output:

            regPercentEx = re.compile(r":\W*(\d+)%$")
            # The file 'file name' has been opened for writing.
            regOutputFileEx = re.compile(r"file (.*?) has")
            indexes = tableView.selectedIndexes()

            processedFiles = 0
            for line in job.output:
                if m := regPercentEx.search(line):
                    n = int(m.group(1))
                    if n < 100:
                        continue
                if f := regOutputFileEx.search(line):
                    processedFiles += 1
                output.insertTextSignal.emit(line, {"log": False})
                # The signals are generated to fast and the History window
                # seems unresponsive
                sleep(0.000001)
            msg = stats(job)

            output.insertTextSignal.emit(msg, {"log": False})

        elif outputType == _ShowKey.errors:

            for analysis in job.errors:

                msg = "Error Job ID: {} ---------------------\n\n".format(
                    job.jobRow[JobKey.ID]
                )

                output.insertTextSignal.emit(
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
                            output.insertTextSignal.emit(line + "\n", {"color": color})
                            sleep(0.000001)
                    else:
                        output.insertTextSignal.emit(m, {"color": SvgColor.red})

                msg = "Error Job ID: {} ---------------------\n\n".format(
                    job.jobRow[JobKey.ID]
                )
                output.insertTextSignal.emit(
                    msg, {"color": SvgColor.red, "appendEnd": True}
                )


class _ShowKey:

    tableView = "tableView"
    proxyModel = "proxyModel"
    output = "output"
    outputType = "outputType"
    errors = "errors"


class _Button:

    FETCHJOBHISTORY = 0
