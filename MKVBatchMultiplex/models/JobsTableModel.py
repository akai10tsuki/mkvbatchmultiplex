"""
TableModel

Class for a table model with horizontal headers

"""

from PySide2.QtCore import Qt, QModelIndex

from vsutillib.pyqt import checkColor, SvgColor

from ..jobs import JobStatus, JobKey
from .TableModel import TableModel

# JOBID, JOBSTATUS, JOBCOMMAND = range(3)


class JobsTableModel(TableModel):
    """
    Subclass of TableModel

    Args:
        TableModel (TableModel): Table Data Model
    """

    def __init__(self, model, jobQueue):
        super(JobsTableModel, self).__init__(model)

        self.jobQueue = jobQueue
        self.model = model

    #
    # Read-Only
    #

    def data(self, index, role):
        """
        TableModel.data() override.

        Use by views and delegates to get table information.

        Arguments:
            index {int} - QModelIndex object that point to a call
            role {int} - what type of data to return. Roles include:
                Qt.DisplayRole, Qt.EditRole, Qt.TextAlignmentRole, Qt.DecorationRole,
                Qt.ToolTipRole, Qt.StatusTipRole, Qt.FontRole, Qt.BackgroundRole
                Qt.ForgroundRole
        """

        if index.isValid():
            if role == Qt.ForegroundRole:
                value = self.dataset.data[index.row()][index.column()].data
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

        superReturn = super().data(index, role)

        return superReturn

    #
    # Resizable Model
    #

    def insertRows(self, position, rows, index=QModelIndex(), data=None):

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
        QAbstractTableModel.setData() override

        Update changes to the model data.

        Arguments:
            index {int} - QModelIndex object that point to a call
            value {object} - value to be set at index
            role {int} - Qt role (default: {Qt.EditRole})
        Returns:
            bool -- True is role is Qt.EditRole and data is updated
                False otherwise
        """

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            super(JobsTableModel, self).setData(index, value, role)

            if value == JobStatus.AddToQueue:
                self.jobQueue.append(row)

            if column == JobKey.Status:
                self.jobQueue.statusChangeSignal.emit(index)

            return True

        return False
