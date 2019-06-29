"""
MKVJobsTableWidget:

Jobs table widget shows jobs and status

context menu on status can change it
"""
# MJT0001


import logging

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (QVBoxLayout, QTableWidget, QMenu, QWidget, QHeaderView,
                               QTableWidgetItem, QAbstractScrollArea)

from ..jobs import JobStatus


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVJobsTableWidget(QWidget):
    """
    Visual representation of job queue

    Also shows status of job
    """
    log = False

    showJobOutput = Signal(int, str, str)

    def __init__(self, parent=None, jobCtrlQueue=None, jobSpCtrlQueue=None):
        super(MKVJobsTableWidget, self).__init__(parent)

        self.parent = parent
        self.ctrlQueue = jobCtrlQueue
        self.spCtrlQueue = jobSpCtrlQueue
        self._initControls()
        self._initLayout()

    def _initControls(self):

        self.jobsTable = JobsTableWidget(self, self.ctrlQueue)

        # table selection change
        self.jobsTable.cellDoubleClicked.connect(self.onDoubleClick)

    def _initLayout(self):

        layout = QVBoxLayout()

        layout.addWidget(self.jobsTable)

        self.setLayout(layout)

    def clearTable(self):
        """Remove Table Rows"""

        self.jobsTable.clearContents()
        self.jobsTable.setRowCount(0)

    def makeConnectionAddJob(self, objSignal):
        """Connect to signals"""

        objSignal.connect(self.jobsTable.addJob)

    def makeConnectionSetJobStatus(self, objSignal):
        """Connect to signals"""

        objSignal.connect(self.jobsTable.setJobStatus)

    @Slot(int, int)
    def onDoubleClick(self, row, col): # pylint: disable=W0613
        """On Single Click Slot"""

        #print("Clicked row = {} col = {}".format(row, col))

        jobID = None
        strTmp = self.jobsTable.getRowJobID(row)
        if strTmp:
            jobID = int(strTmp)
        status = self.jobsTable.getRowStatus(row)
        command = self.jobsTable.getRowCommand(row)

        if jobID:
            self.showJobOutput.emit(jobID, status, command)


class JobsTableWidget(QTableWidget):
    """Jobs Table"""

    updateJobStatus = Signal(int, str, bool)

    def __init__(self, parent=None, ctrlQueue=None):
        super(JobsTableWidget, self).__init__(parent)

        self.parent = parent
        self.ctrQueue = ctrlQueue
        self.actions = JobStatus()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Jobs ID", "Status", "Description"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setWordWrap(False)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents
        )
        self.verticalHeader().hide()

    def getRowJobID(self, row):
        """Get jobID by row"""

        totalRows = self.rowCount()

        jobID = None
        if 0 <= row < totalRows:
            if self.item(row, 0):
                jobID = self.item(row, 0).text()

        return jobID

    def getRowStatus(self, row):
        """Get status by row"""

        totalRows = self.rowCount()

        status = None
        if 0 <= row < totalRows:
            if self.item(row, 1):
                status = self.item(row, 1).text()

        return status

    def getRowCommand(self, row):
        """Get status by row"""

        totalRows = self.rowCount()

        command = None
        if 0 <= row < totalRows:
            if self.item(row, 2):
                command = self.item(row, 2).text()

        return command

    def setRowStatus(self, row, status):
        """Set status by row"""

        totalRows = self.rowCount()

        if 0 <= row < totalRows:
            #item = QTableWidgetItem(status)
            #self.setItem(row, 1, item)
            strJobID = self.getRowJobID(row)
            if strJobID:
                jobID = int(strJobID)
                self.updateJobStatus.emit(jobID, status, True)

    def setRowJobID(self, row, jobID):
        """Set status by row"""

        totalRows = self.rowCount()

        if 0 <= row < totalRows:
            item = QTableWidgetItem(jobID)
            self.setItem(row, 0, item)

    def contextMenuEvent(self, event):
        """Context Menu"""

        row = self.rowAt(event.pos().y())
        col = self.columnAt(event.pos().x())
        totalRows = self.rowCount()

        status = self.getRowStatus(row)
        #jobID = self.getRowJobID(row)

        #print("row = {} col = {} status = {} job = {}".format(row, col, status, jobID))

        if (0 <= row < totalRows) and (col == 1):

            menu = QMenu()
            skipAction = None
            waitingAction = None

            if status == self.actions.Waiting:
                skipAction = menu.addAction(self.actions.Skip)
            elif status in [self.actions.Skip, self.actions.Aborted,
                            self.actions.Abort, self.actions.Done]:
                waitingAction = menu.addAction(self.actions.Waiting)
            elif status == self.actions.Running:
                abortAction = menu.addAction(self.actions.Abort)

            if not menu.isEmpty():
                action = menu.exec_(self.mapToGlobal(event.pos()))

                if action == skipAction:
                    self.setRowStatus(row, self.actions.Skip)
                elif action == waitingAction:
                    self.setRowStatus(row, self.actions.Waiting)
                elif action == abortAction:
                    self.setRowStatus(row, self.actions.Abort)
                    if self.spCtrQueue is not None:
                        self.spCtrlQueue.put(self.actions.AbortJob)

    def resizeEvent(self, event):

        super(JobsTableWidget, self).resizeEvent(event)

        header = self.horizontalHeader()

        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        width = header.sectionSize(2)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.resizeSection(2, width)

    @Slot(int, str, str)
    def addJob(self, jobID, status, cmd):
        """Add Job to Table"""

        item0 = QTableWidgetItem(str(jobID))
        item1 = QTableWidgetItem(status)
        item2 = QTableWidgetItem(cmd)
        item0.setFlags(Qt.ItemIsEnabled)
        item1.setFlags(Qt.ItemIsEnabled)
        item2.setFlags(Qt.ItemIsEnabled)
        item2.setToolTip(cmd)

        rowNumber = self.rowCount()
        self.insertRow(rowNumber)
        self.setItem(rowNumber, 0, item0)
        self.setItem(rowNumber, 1, item1)
        self.setItem(rowNumber, 2, item2)

    @Slot(int, str)
    def setJobStatus(self, jobID, status):
        """Update the job status"""

        for row in list(range(self.rowCount())):

            rowJobID = self.getRowJobID(row)
            #print("Lookup Row = {} Job = {}".format(row, rowJobID))
            if int(rowJobID) == jobID:

                self.setItem(row, 1, QTableWidgetItem(status))
