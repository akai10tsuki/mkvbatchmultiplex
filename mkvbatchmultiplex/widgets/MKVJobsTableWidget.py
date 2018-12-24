#!/usr/bin/env python3

"""
MKVOutputWidget:

Queue Management

Status:
    Waiting
    Running
    Stopped
    Skip
    Finished

JT001
"""

import logging

from PyQt5.QtCore import QMutex, QMutexLocker, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QVBoxLayout, QTableWidget, QMenu, QWidget,
                             QTableWidgetItem, QAbstractScrollArea)

from mkvbatchmultiplex.jobs import JobStatus

MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

class MKVJobsTableWidget(QWidget):
    """
    Visual representation of job queue

    Also shows status of job
    """

    showJobOutput = pyqtSignal(int, str, str)

    def __init__(self, parent=None, ctrlQueue=None):
        super(MKVJobsTableWidget, self).__init__(parent)

        self.parent = parent
        self.ctrlQueue = ctrlQueue
        self._initControls()
        self._initLayout()

    def _initControls(self):

        self.jobsTable = JobsTableWidget(self, self.ctrlQueue)

        # table selection change
        self.jobsTable.cellClicked.connect(self.onClick)

    def _initLayout(self):

        layout = QVBoxLayout()

        layout.addWidget(self.jobsTable)

        self.setLayout(layout)

    def clearTable(self):
        """Remove Table Rows"""

        self.jobsTable.clearContents()
        self.jobsTable.setRowCount(0)

    def makeConnection0(self, objSignal):
        """Connect to signals"""

        objSignal.connect(self.jobsTable.addJob)

    def makeConnection1(self, objSignal):
        """Connect to signals"""

        objSignal.connect(self.jobsTable.setJobStatus)

    @pyqtSlot(int, int)
    def onClick(self, row, col): # pylint: disable=W0613
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

    updateJobStatus = pyqtSignal(int, str, bool)

    def __init__(self, parent=None, ctrlQueue=None):
        super(JobsTableWidget, self).__init__(parent)

        self.parent = parent
        self.ctrQueue = ctrlQueue
        self.actions = JobStatus()

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Jobs ID", "Status", "Description"])
        self.horizontalHeader().setStretchLastSection(True)
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
                    if self.ctrQueue is not None:
                        self.ctrQueue.put(self.actions.Abort)


    @pyqtSlot(int, str, str)
    def addJob(self, jobID, status, cmd):
        """Add Job to Table"""

        with QMutexLocker(MUTEX):

            item0 = QTableWidgetItem(str(jobID))
            item1 = QTableWidgetItem(status)
            item2 = QTableWidgetItem(cmd)
            item0.setFlags(Qt.ItemIsEnabled)
            item1.setFlags(Qt.ItemIsEnabled)
            item2.setFlags(Qt.ItemIsEnabled)

            rowNumber = self.rowCount()
            self.insertRow(rowNumber)
            self.setItem(rowNumber, 0, item0)
            self.setItem(rowNumber, 1, item1)
            self.setItem(rowNumber, 2, item2)

    @pyqtSlot(int, str)
    def setJobStatus(self, jobID, status):
        """Update the job status"""

        with QMutexLocker(MUTEX):

            for row in list(range(self.rowCount())):

                rowJobID = self.getRowJobID(row)
                #print("Lookup Row = {} Job = {}".format(row, rowJobID))
                if int(rowJobID) == jobID:

                    self.setItem(row, 1, QTableWidgetItem(status))
