"""
TableModel

Class for a table model with horizontal headers

"""

from PySide2.QtCore import Qt, QModelIndex

from vsutillib.pyqt import SvgColor

#from ..dataset import TableData, tableHeaders
from ..jobs import JobStatus, JobKey, jobStatusTooltip
from .TableModel import TableModel

# JOBID, JOBSTATUS, JOBCOMMAND = range(3)


class JobsTableModel(TableModel):
    """
    Subclass of the QAbstractTableModel.

    This class holds the table data and header information Overrides the
    methods:
        - data(index, role)
        - insertRows(position, rows, index, data)
        - setData(index, value, role)

    The class is defined in order to interact with the job queue for some
    operations on the model/view

    Args:
        **tableData** (TableData): Table Data for the model

        **jobQueue** (deque): job queue
    """

    def __init__(self, tableData, jobQueue):
        super().__init__(parent=None, tableData=tableData)

        self.jobQueue = jobQueue

    #
    # Read-Only
    #

    def data(self, index, role):
        """
        TableModel.data() override.

        Use by views and delegates to get table information.

        Arguments:
            **index** (QModelIndex) - QModelIndex object that point to a cell

            **role** (int) - what type of data to return.

        Roles include:
            Qt.DisplayRole, Qt.EditRole, Qt.TextAlignmentRole, Qt.DecorationRole,
            Qt.ToolTipRole, Qt.StatusTipRole, Qt.FontRole, Qt.BackgroundRole
            Qt.ForgroundRole
        """

        if index.isValid():
            row = index.row()
            column = index.column()

            if role == Qt.ForegroundRole:
                if column == JobKey.Status:
                    value = self.dataset.data[row][column].cell
                    if value == JobStatus.Done:
                        return SvgColor.cyan
                    elif value == JobStatus.Running:
                        return SvgColor.green
                    elif value in [
                        JobStatus.Abort,
                        JobStatus.Aborted,
                        JobStatus.AbortForced,
                        JobStatus.AbortJob,
                        JobStatus.AbortJobError,
                        JobStatus.Stop,
                        JobStatus.Stopped,
                    ]:
                        return SvgColor.red
                    elif value in [
                        JobStatus.Blocked,
                        JobStatus.DoneWithError,
                        JobStatus.Error,
                    ]:
                        return SvgColor.tomato
                    elif value in [JobStatus.Skip, JobStatus.Skipped]:
                        return SvgColor.yellow
                    elif value in [JobStatus.Waiting]:
                        return SvgColor.yellowgreen

            if role == Qt.ToolTipRole:
                if column == JobKey.Status:
                    value = self.dataset.data[row][column].cell
                    return jobStatusTooltip(value)

        superReturn = super().data(index, role)

        return superReturn

    #
    # Resizable Model
    #
    def insertRows(self, position, rows, index=QModelIndex(), data=None):
        """
        TableDataModel.insertRows() override

        Insert the number of rows starting at position.  And add the jobs to the
        jobs queue.

        Args:
            **position** (int): starting position for rows insertion

            **rows** (int): number of rows to insert

            **index** (QModelIndex, optional): index to row at position. Defaults
            to QModelIndex().

            **data** (list, optional): If data is not None the information is used
            to fill the data on the new rows. Defaults to None.

        Returns:
            bool: True if transaction successful. False otherwise.
        """

        rc = super(JobsTableModel, self).insertRows(position, rows, index, data=data)

        if rc:
            for r in range(0, rows):
                jobRow = position + r
                self.jobQueue.append(jobRow)
            self.jobQueue.statusChangeSignal.emit(index)

        return rc

    #
    # Editable
    #
    def setData(self, index, value, role=Qt.EditRole):
        """
        TableDataModel.setData() override

        Update changes to the model data.

        Arguments:
            **index** (int) - QModelIndex object that point to a cell

            **value** (object) - value to be set at index

            **role** (int) - Qt role (default: {Qt.EditRole})

        Returns:
            bool -- True is role is Qt.EditRole and data is updated
                False otherwise
        """

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            super().setData(index, value, role)

            if value == JobStatus.AddToQueue:
                self.jobQueue.append(row)

            if column == JobKey.Status:
                self.jobQueue.statusChangeSignal.emit(index)

            return True

        return False
