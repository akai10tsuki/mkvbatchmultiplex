"""
TableModel

Class for a table model with horizontal headers

"""

from PySide2.QtCore import Qt, QModelIndex

from .TableModel import TableModel
from ..jobs import JobStatus

JOBID, JOBSTATUS, JOBCOMMAND = range(3)


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

    def insertRows(self, position, rows, index=QModelIndex(), data=None):

        rc = super(JobsTableModel, self).insertRows(position, rows, index, data=data)

        if rc:
            for r in range(0, rows):
                jobRow = position + r
                self.jobQueue.append(jobRow)

        return rc

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

            super(JobsTableModel, self).setData(index, value, role)

            if value == JobStatus.AddToQueue:
                self.jobQueue.append(row)

            return True

        return False
