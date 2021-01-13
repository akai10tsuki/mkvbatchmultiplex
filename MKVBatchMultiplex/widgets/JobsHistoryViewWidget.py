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

# import pprint

from datetime import datetime, timedelta

# from pprint import pprint
from time import sleep

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QTextCursor
from PySide2.QtWidgets import (
    QDialogButtonBox,
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

from vsutillib.misc import strFormatTimeDelta

from ..config import data as config
from ..config import ConfigKey

from .ProjectInfoDialogWidget import ProjectInfoDialogWidget

from ..jobs import (
    JobHistoryKey,
    JobKey,
    SqlJobsTable,
    JobsTableKey,
)
from ..utils import Text

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

    pasteCommandSignal = Signal(str)
    updateAlgorithmSignal = Signal(int)

    def __init__(self, parent=None, groupTitle=None, log=None):
        super().__init__(parent=None, tabWidgetChild=self)

        self.parent = parent

        self.tableView = JobsHistoryView(self, groupTitle)
        self.search = SearchTextDialogWidget(self)
        self.infoDialog = ProjectInfoDialogWidget(self)
        self._initUI(groupTitle)
        self._initHelper()

        self.log = log

    def _initUI(self, groupTitle):

        grid = QGridLayout()
        self.grpGrid = QGridLayout()
        self.grpBox = QGroupBox(groupTitle)

        self.output = QOutputTextWidget(self)

        btnFetchJobHistory = QPushButtonWidget(
            Text.txt0242,
            function=self.fetchJobHistory,
            margins="  ",
            toolTip=Text.txt0251,
        )
        btnSearchText = QPushButtonWidget(
            Text.txt0243,
            function=self.searchText,
            margins="  ",
            toolTip=Text.txt0254,
        )
        btnClearSelection = QPushButtonWidget(
            Text.txt0248,
            function=self.clearSelection,
            margins="  ",
            toolTip=Text.txt0256,
        )
        btnClearOutput = QPushButtonWidget(
            Text.txt0255,
            function=self.clearOutputWindow,
            margins="  ",
            toolTip=Text.txt0257,
        )
        btnShowInfo = QPushButtonWidget(
            Text.txt0249,
            function=self.showInfo,
            margins="  ",
            toolTip=Text.txt0258,
        )
        btnSelectAll = QPushButtonWidget(
            Text.txt0247,
            function=self.selectAll,
            margins="  ",
            toolTip=Text.txt0259,
        )
        btnPrint = QPushButtonWidget(
            Text.txt0246,
            function=self.printDataset,
            margins="  ",
            toolTip=Text.txt0260,
        )
        btnShowOutput = QPushButtonWidget(
            Text.txt0244,
            function=lambda: self.showOutput(_ShowKey.output),
            margins="  ",
            toolTip=Text.txt0262,
        )
        btnShowOutputErrors = QPushButtonWidget(
            Text.txt0245,
            function=lambda: self.showOutput(_ShowKey.errors),
            margins="  ",
            toolTip=Text.txt0262,
        )

        self.btnGrid = QHBoxLayout()
        self.btnGrid.addWidget(btnFetchJobHistory)
        self.btnGrid.addWidget(btnSearchText)
        self.btnGrid.addWidget(btnShowOutput)
        self.btnGrid.addWidget(btnShowOutputErrors)
        self.btnGrid.addWidget(btnShowInfo)
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

        self.btnGrid.itemAt(_Button.SHOWOUTPUT).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.SHOWOUTPUTERRORS).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.SHOWINFO).widget().setEnabled(False)
        # self.btnGrid.itemAt(_Button.PRINT).widget().hide()
        self.btnGrid.itemAt(_Button.PRINT).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.CLEARSELECTION).widget().setEnabled(False)
        self.btnGrid.itemAt(_Button.CLEAROUTPUT).widget().setEnabled(False)

        # self.cmdLine.textChanged.connect(self.analysisButtonState)
        self.output.textChanged.connect(self.clearOutputButtonState)
        self.tableView.clicked.connect(self.rowsClicked)
        self.tableView.clickedOutsideRowsSignal.connect(self.buttonsState)
        self.tableView.rowCountChangedSignal.connect(self.buttonsState)

        # Just Ok on info dialog
        self.infoDialog.ui.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

    @Slot()
    def setLanguage(self):
        """
        setLanguage set labels according to locale
        """

        for index in range(self.btnGrid.count()):
            widget = self.btnGrid.itemAt(index).widget()
            if isinstance(widget, QPushButtonWidget):
                widget.setLanguage()
                #widget.setText("  " + _(widget.originalText) + "  ")
                #widget.setToolTip(widget.toolTip)

        self.grpBox.setTitle(_(Text.txt0130))
        self.tableView.model.setHeaderData(
            _JobHKey.ID, Qt.Horizontal, "  " + _(Text.txt0131) + "  "
        )
        self.tableView.model.setHeaderData(
            _JobHKey.Date, Qt.Horizontal, "    " + _(Text.txt0240) + "    "
        )
        self.tableView.model.setHeaderData(
            _JobHKey.Status, Qt.Horizontal, "    " + _(Text.txt0132) + "    "
        )
        self.tableView.model.setHeaderData(
            _JobHKey.Command, Qt.Horizontal, _(Text.txt0133)
        )

    @Slot(int, int)
    def buttonsState(self, oldCount, newCount):
        """
        buttonsState enable disable buttons according to row count

        Args:
            oldCount (int): old row count number
            newCount (int): new row count number
        """

        if newCount <= 0:
            # print("View Widget Entering buttonsState 0 rows ...")
            self.btnGrid.itemAt(_Button.CLEARSELECTION).widget().setEnabled(False)
            self.btnGrid.itemAt(_Button.PRINT).widget().setEnabled(False)
            self.btnGrid.itemAt(_Button.SHOWINFO).widget().setEnabled(False)
            self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(False)
            self.btnGrid.itemAt(_Button.SHOWOUTPUT).widget().setEnabled(False)
            self.btnGrid.itemAt(_Button.SHOWOUTPUTERRORS).widget().setEnabled(False)
            if oldCount < 0:
                totalRows = self.tableView.model.rowCount()
                if totalRows > 0:
                    self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(True)
        else:
            totalRows = self.tableView.model.rowCount()
            totalSelectedRows = self.tableView.selectedRowsCount()

            # print(
            #    (
            #        f"View Widget Entering buttonsState total rows {totalRows} "
            #        f"total selected rows {totalSelectedRows} selected ..."
            #    )
            # )

            if totalRows == 0:
                self.buttonsState(0, 0)
            else:
                self.btnGrid.itemAt(_Button.PRINT).widget().hide()
                self.btnGrid.itemAt(_Button.SHOWINFO).widget().setEnabled(False)
                self.btnGrid.itemAt(_Button.SHOWOUTPUT).widget().setEnabled(False)
                self.btnGrid.itemAt(_Button.SHOWOUTPUTERRORS).widget().setEnabled(False)
                if totalSelectedRows == 0:
                    self.btnGrid.itemAt(_Button.CLEARSELECTION).widget().setEnabled(
                        False
                    )
                    self.btnGrid.itemAt(_Button.PRINT).widget().setEnabled(False)
                    self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(False)
                elif totalSelectedRows == 1:
                    self.btnGrid.itemAt(_Button.CLEARSELECTION).widget().setEnabled(
                        True
                    )
                    self.btnGrid.itemAt(_Button.SHOWINFO).widget().setEnabled(True)
                    self.btnGrid.itemAt(_Button.SHOWOUTPUT).widget().setEnabled(True)
                    self.btnGrid.itemAt(_Button.SHOWOUTPUTERRORS).widget().setEnabled(
                        True
                    )
                if totalSelectedRows == totalRows:
                    self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(False)
                else:
                    self.btnGrid.itemAt(_Button.SELECTALL).widget().setEnabled(True)

    def clearOutputButtonState(self):
        """Set clear button state"""

        if self.output.toPlainText() != "":
            self.btnGrid.itemAt(_Button.CLEAROUTPUT).widget().setEnabled(True)
        else:
            self.btnGrid.itemAt(_Button.CLEAROUTPUT).widget().setEnabled(False)

    @Slot()
    def rowsClicked(self):
        totalRows = self.tableView.model.rowCount()
        self.buttonsState(0, totalRows)

    def clearOutputWindow(self):
        """
        clearOutputWindow clear the command output window
        """

        self.output.clear()

    def clearSelection(self):

        self.tableView.clearSelection()
        self.rowsClicked()

    def selectAll(self):

        self.tableView.selectAll()
        self.rowsClicked()

    def fetchJobHistory(self):
        """Get the log records from database"""

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

        if jobsDB:
            rows = jobsDB.fetchJob(0)
            if rows:
                totalRows = self.tableView.model.rowCount()
                if totalRows > 0:
                    self.tableView.model.removeRows(0, totalRows)
                fillRows(self, rows)

        jobsDB.close()

    def searchText(self):
        """Do full text search"""

        jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

        if jobsDB:
            rows = self.search.searchText(jobsDB)
            if rows:
                totalRows = self.tableView.model.rowCount()
                if totalRows > 0:
                    self.tableView.model.removeRows(0, totalRows)
                fillRows(self, rows)

        jobsDB.close()

    def showOutput(self, outputType):

        qtRunFunctionInThread(
            showOutputLines,
            tableView=self.tableView,
            proxyModel=self.tableView.proxyModel,
            output=self.output,
            outputType=outputType,
            funcStart=self.parent.progressSpin.startAnimation,
            funcFinished=self.parent.progressSpin.stopAnimation,
        )

    def printDataset(self):
        """
        printDataset development debug
        """
        # QApplication.setPalette(darkPalette())
        dataset = self.tableView.model.dataset

        for r in range(0, len(dataset)):
            self.output.insertTextSignal.emit(
                "Row {} ID {} Status {}\n".format(
                    r, dataset[r, JobKey.ID], dataset[r, JobKey.Status]
                ),
                {"log": False},
            )

        self.output.insertTextSignal.emit("\n", {"log": False})

    def showInfo(self):
        """Refresh jobs records"""

        indexes = self.tableView.selectionModel().selectedRows()

        if len(indexes) == 1:

            jobsDB = SqlJobsTable(config.get(ConfigKey.SystemDB))

            index = self.tableView.proxyModel.mapToSource(indexes[0])
            model = self.tableView.proxyModel.sourceModel()

            row = index.row()
            # column = index.column()
            # job = model.dataset.data[row][
            #    JobHistoryKey.Status
            # ].obj  # TODO: change to status
            rowid = model.dataset.data[row][JobHistoryKey.ID].obj
            jobID = model.dataset.data[row][JobHistoryKey.ID].cell
            if rowid is not None:
                records = jobsDB.fetchJob(
                    {"rowid": rowid},
                    JobsTableKey.projectName,
                    JobsTableKey.projectInfo,
                )
                if records:
                    record = records.fetchone()
                    # print(f"Houston we have a record.\n\nProject Name: [{record}]")
                    title = self.infoDialog.windowTitle()
                    self.infoDialog.setWindowTitle(title + " - " + str(jobID))
                    self.infoDialog.name = record[1]
                    self.infoDialog.description = record[2]
                    self.infoDialog.ui.teDescription.moveCursor(QTextCursor.Start)

                    self.infoDialog.getProjectInfo()
                    name, desc = self.infoDialog.info
                    records = jobsDB.update(
                        {"rowid": rowid},
                        (
                            JobsTableKey.projectName,
                            JobsTableKey.projectInfo,
                        ),
                        name,
                        desc,
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
            if job.startTime is None:
                dt = "0000-00-00 00:00:00"
            else:
                dt = datetime.fromtimestamp(job.startTime)
                dt = dt.isoformat(sep=" ")
            viewRow[JobHistoryKey.ID] = [
                row[JobsTableKey.IDIndex],
                "",
                row[JobsTableKey.rowidIndex],
            ]
            viewRow[JobHistoryKey.Date] = [
                dt,
                "Date job was executed",
                None,
            ]
            viewRow[JobHistoryKey.Status] = [
                job.jobRow[JobKey.Status],
                "",
                job,
            ]
            viewRow[JobHistoryKey.Command] = [
                job.jobRow[JobKey.Command],
                job.jobRow[JobKey.Command],
                None,
            ]
            self.tableView.model.insertRows(rowNumber, 1, data=viewRow)
            rowNumber += 1


def stats(job):
    """Display stats format"""

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
    """
    showOutputLines - List the output line for the job try to mimic the output
    as when it ran. Not that easy many functions write the output.
    """

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
        job = model.dataset.data[row][
            JobHistoryKey.Status
        ].obj  # TODO: change to status
        rowid = model.dataset.data[row][JobHistoryKey.ID].obj
        if job is None:
            # print("Fetching Job")
            records = jobsDB.fetchJob({"rowid": rowid}, JobsTableKey.job)
            if records:
                record = records.fetchone()
                job = pickle.loads(zlib.decompress(record[1]))
                model.dataset.data[row][JobHistoryKey.Status].obj = copy.deepcopy(job)
            else:
                msg = "Information cannot be read."
                output.insertTextSignal.emit(msg, {"log": False})
                return

        if outputType == _ShowKey.output:

            regPercentEx = re.compile(r":\W*(\d+)%$")
            # The file 'file name' has been opened for writing.
            # TODO: how to do it without locale dependency
            regOutputFileEx = re.compile(r"file (.*?) has")
            indexes = tableView.selectedIndexes()

            processedFiles = 0
            for line, arguments in job.output:
                if m := regPercentEx.search(line):
                    n = int(m.group(1))
                    if n < 100:
                        continue
                if f := regOutputFileEx.search(line):  # pylint: disable=unused-variable
                    processedFiles += 1
                arguments["log"] = False
                output.insertTextSignal.emit(line, arguments)
                # The signals are generated to fast and the History window
                # seems unresponsive
                sleep(0.000001)

            for line in job.oCommand.strCommands:
                output.insertTextSignal.emit(line, {"log": False})
                # The signals are generated to fast and the History window
                # seems unresponsive
                sleep(0.000001)

            msg = stats(job)

            output.insertTextSignal.emit(msg, {"log": False})

        elif outputType == _ShowKey.errors:

            for analysis in job.errors:
                if isinstance(analysis[1], dict):
                    output.insertTextSignal.emit(analysis[0], analysis[1])
                    sleep(0.000001)
                else:
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
                                output.insertTextSignal.emit(
                                    line + "\n", {"color": color, "log": False}
                                )
                                sleep(0.000001)
                        else:
                            output.insertTextSignal.emit(
                                m, {"color": SvgColor.red, "log": False}
                            )
                            sleep(0.000001)
        jobsDB.close()


class _ShowKey:

    tableView = "tableView"
    proxyModel = "proxyModel"
    output = "output"
    outputType = "outputType"
    errors = "errors"


class _Button:

    FETCHJOBHISTORY = 0

    SHOWOUTPUT = 2
    SHOWOUTPUTERRORS = 3
    SHOWINFO = 4

    PRINT = 6
    SELECTALL = 7
    CLEARSELECTION = 8
    CLEAROUTPUT = 9


class _JobHKey:

    ID = 0
    Date = 1
    Status = 2
    Command = 3
