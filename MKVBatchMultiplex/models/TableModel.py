"""
TableModel

Class for a table model with horizontal headers

"""
# JTM0001

########################################################################
# Documentation extracts from:
#    https://doc.qt.io/qtforpython/overviews/model-view-programming.html
#
# The official QT Python documentation
########################################################################
#
##################
# Read-Only Models
##################
#
# Must implement the following methods:
#
# flags(self, index) - Se bellow
#
# data(self, index, role) - Used to supply item data to views and delegates. Generally, models
#   only need to supply data for **DisplayRole** and any application-specific user roles, but
#   it is also good practice to provide data for **ToolTipRole**, **AccessibleTextRole**, and
#   **AccessibleDescriptionRole**. See the ItemDataRole enum documentation for information
#   about the types associated with each role.
#
# headerData(self, section, orientation, role) - Provides views with information to show in
#   their headers. The information is only retrieved by views that can display header
#   information.
#
# rowCount(self, parent) - Provides the number of rows of data exposed by the model.
#
# These four functions must be implemented in all types of model, including list models
# (QAbstractListModel subclasses) and table models (QAbstractTableModel subclasses).
# Additionally, the following functions must be implemented in direct subclasses of
# QAbstractTableModel and QAbstractItemModel:
#
# columnCount(self, parent) - Provides the number of columns of data exposed by the model.
#   List models do not provide this function because it is already implemented in
#   QAbstractListModel.
#
#######################
# Editable Items Models
#######################
#
# flags(self, index) - se bellow
#
# setData(self, index, value, role=Qt.EditRole) - Used to modify the item of data associated
#   with a specified model index. To be able to accept user input, provided by user interface
#   elements, this function must handle data associated with EditRole . The implementation may
#   also accept data associated with many different kinds of roles specified by ItemDataRole.
#   After changing the item of data, models must emit the dataChanged() signal to inform other
#   components of the change.
#
# setHeaderData(self, section, orientation, value, role=QtCore.Qt.EditRole) - Used to modify
#   horizontal and vertical header information. After changing the item of data, models must
#   emit the headerDataChanged() signal to inform other components of the change.
#
#
# flags(self, index) - Used by other components to obtain information about each item provided
#   by the model.  In many models, the combination of flags should include:
#
#       For Read-Only
#
#           ItemIsEnabled
#           ItemIsSelectable
#
#       For Editable items
#
#           ItemIsEditable
#
#           in addition to the values applied to items in a read-only model.
#
#################
# Resizable Model
#################
#
# insertRows(self, position, rows, index=QModelIndex()) - Used to add new rows and items of
#   data to all types of model. Implementations must call beginInsertRows() before inserting
#   new rows into any underlying data structures, and call endInsertRows() immediately
#   afterwards.
#
# removeRows(self, position, rows, index=QModelIndex()) - Used to remove rows and the items
#   of data they contain from all types of model. Implementations must call beginRemoveRows()
#   before rows are removed from any underlying data structures, and call endRemoveRows()
#   immediately afterwards .
#
# insertColumns(self, position, columns, index=QModelIndex()) - Used to add new columns and
#   items of data to table models and hierarchical models. Implementations must call
#   beginInsertColumns() before inserting new columns into any underlying data structures, and
#   call endInsertColumns() immediately afterwards.
#
# removeColumns(self, position, columns, index=QModelIndex()) - Used to remove columns and the
#   items of data they contain from table models and hierarchical models. Implementations must
#   call beginRemoveColumns() before columns are removed from any underlying data structures,
#   and call endRemoveColumns() immediately afterwards.
#

# pylint: disable=unused-argument


from PySide2.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel, QModelIndex

JOBID, JOBSTATUS, JOBCOMMAND = range(3)


class TableModel(QAbstractTableModel):
    """Model for table view

    Arguments:
        QAbstractTableModel {Class in QtCore} -- Base class for a table model

    Returns:
        class JobsTableModel -- table model for our view
    """

    def __init__(self, tableData):
        """
        Subclass of the QAbstractTableModel.

        This class holds the table data and header information Overrides the methods:
            data(self, index, role)
            setData(self, index, value, role=Qt.EditRole)
            headerData(self, section, orientation, role)
            flags(self, index)

        Arguments:
            tableData {TableData} -- Class that supplies the header and row information
        """

        super(TableModel, self).__init__()

        self.dataset = tableData

    ####################
    # Item Data Handling
    ####################

    #
    # Read-Only Items methods
    #

    def headerData(self, section, orientation, role):
        """
        QAbstractTableModel.headerData override.

        Data to display in the header on the QTableView

        Arguments:
            section {int} -- row or column number
            orientation {int} -- Qt.Horizontal for columns headers or Qt.Vertical for row headers
            role {int} -- what type of data to return. Roles include:
                Qt.DisplayRole, Qt.TextAlignmentRole, Qt.ToolTipRole, Qt.StatusTipRole, Qt.FontRole,
                Qt.BackgroundRole

        Returns:
            int, str -- Qt.Alignment flag or Column label Rows not implemented
        """

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.dataset[section]

            if orientation == Qt.Vertical:
                # For the implementation of row headers
                pass

        elif role == Qt.ToolTipRole:
            if orientation == Qt.Horizontal:
                return self.dataset.headers[section].attribute["ToolTip"]

            if orientation == Qt.Vertical:
                # For the implementation of row headers
                pass

        elif role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                alignment = self.dataset.headers[section].attribute["Alignment"]

                if alignment == "right":
                    return Qt.AlignRight

                if alignment == "left":
                    return Qt.AlignLeft

                return Qt.AlignCenter

        elif role == Qt.InitialSortOrderRole:
            if orientation == Qt.Horizontal:
                return Qt.AscendingOrder

        return None

    def data(self, index, role):
        """
        QAbstractTableModel.data() override.

        Use by views and delegates to get table information.

        Arguments:
            index {int} - QModelIndex object that point to a call
            role {int} - what type of data to return. Roles include:
                Qt.DisplayRole, Qt.EditRole, Qt.TextAlignmentRole, Qt.DecorationRole,
                Qt.ToolTipRole, Qt.StatusTipRole, Qt.FontRole, Qt.BackgroundRole
        """

        if index.isValid():
            row = index.row()
            column = index.column()

            if role in [Qt.DisplayRole, Qt.EditRole]:
                if self.dataset.data[row][column].cell != "":
                    return self.dataset.headers[column].attribute["CastFunction"](
                        self.dataset.data[row][column].cell
                    )

            elif role == Qt.ToolTipRole:
                toolTip = None

                # if column == JOBCOMMAND:
                toolTip = self.dataset.data[row][column].toolTip

                if toolTip:
                    return toolTip

            elif role == Qt.TextAlignmentRole:
                if self.dataset.headers[column].attribute["Alignment"] == "right":
                    return Qt.AlignRight

                if self.dataset.headers[column].attribute["Alignment"] == "center":
                    return Qt.AlignCenter

                return Qt.AlignLeft

        return None

    def rowCount(self, parent=None):
        """Returns the number of rows in the model."""

        return len(self.dataset)

    def columnCount(self, parent=None):
        """Returns the number of columns in the model."""

        return len(self.dataset.headers)

    #
    # Editable Items methods
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
            self.dataset.setData(index, value)
            self.dataChanged.emit(index, index)

            return True

        return False

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):

        if role == Qt.EditRole:
            if orientation == Qt.Horizontal:
                self.dataset[section] = value
                self.headerDataChanged.emit(orientation, section, section)

    #
    # Used by Editable and Read-Only Items Models
    #

    def flags(self, index):
        """
        QAbstractTableModel.flags() override

        Set whetter a cell is enabled, selectable and/or editable.

        Arguments:
            index {int} - QModelIndex object that point to a call
        Returns:
            {int} - Qt flag ItemIsEnabled and ItemIsSelectable
        """

        #
        # Every cell is enable and selectable
        # TODO: use header to control this by Column
        #

        if not index.isValid():
            return Qt.ItemIsDropEnabled

        if index.column() == 1:
            # if status column
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    #
    # Resizable Model
    #
    def insertRows(self, position, rows, index=QModelIndex(), data=None):

        rowCount = self.rowCount()
        dataCount = 0 if data is None else len(data)

        if position <= rowCount:
            self.beginInsertRows(index, position, position + rows - 1)

            for row in range(0, rows):
                if dataCount >= rows:
                    if rows > 1:
                        newRow = data[row]
                    else:
                        newRow = data
                else:
                    newRow = [None, None, None]

                self.dataset.insertRow(position + row, newRow)

            self.endInsertRows()

            return True

        return False

    def removeRows(self, position, rows, parent=QModelIndex()):

        if position < 0:
            return False

        rowCount = self.rowCount()

        if position <= rowCount:
            self.beginRemoveRows(parent, position, position + rows - 1)
            # del self.dataset[position:rows + 1] verify

            # delete rows starting from highest index
            # in the range going backwards
            for row in range(rows - 1, -1, -1):
                self.dataset.removeRow(position + row)

            self.endRemoveRows()

        return True

    #
    # Enable Drag and Drop
    #
    def supportedDropActions(self):

        return Qt.CopyAction | Qt.MoveAction

    def canDropMimeData(self, data, action, row, col, parent):

        if not data.hasFormat("text/plain"):
            return False

        return True


class TableProxyModel(QSortFilterProxyModel):
    """Proxy model
    """

    def __init__(self, model):
        """
        Subclass of the QSortFilterProxyModel. This class allows the table view to interact with
        the model indirectly via a middle-mas proxy that sorts or filters the table. It
        re-implements the filterAcceptsRow method to allow flexibility on how data are filtered,
        including filtering base on multiple columns. Re-implement filterAcceptsRow() method as
        desired. Use self.sourceModel() to refer to the underlying table model. Use
        mapToSource(index) to convert an index in the proxy model to an index in the underlying
        model, allowing you to access the respective dataset via row and column index methods.

        :param model: TableModel object holding the underlying model
        """

        super().__init__()

        self.setSourceModel(model)
        # Can be changed, added to and used for filterAcceptsRow filtering
        self.filterConditions = {"Remove": []}

    def filterAcceptsRow(self, sourceRow, sourceParent):
        """
        Returns True if the row matches required conditions to remain in the filtered table,
        False to remove the row

        :param sourceRow: int, the row index in the source model
        :param sourceParent: parent object of source model
        """

        if sourceRow in self.filterConditions["Remove"]:
            return False

        for column, conditions in self.filterConditions.items():
            if column == "Remove":
                if sourceRow in conditions:
                    return False

            for i, columnName in enumerate(self.sourceModel().dataset.headerName):
                if columnName == column:
                    if self.sourceModel().dataset[sourceRow, i] not in conditions:
                        return False

        return True

    def addFilterCondition(self, columnName, conditions):
        """
        Specifies a list of values for a specified column which are to be included in a filtered
        table. This replaces any previous filter on the same column but does not reset any other
        filters. Use reset_filters() to reset all filters. Re-implement this function if you want
        more complicated methods of determining filter conditions, for example if you want to add
        a value to the already-existing list of conditions for a given column rather than replacing
        the conditions list entirely, or if you want to specify to exclude specified values instead
        of including them.

        :param columnName: str, name of column, must be included in the columns list of the source
        model
        :param conditions: list of values to be included a filter of the specified column
        """

        self.filterConditions[columnName] = conditions
        self.setFilterFixedString("")

    def resetFilters(self):
        """Removes all filter conditions and returns the table to its original unfiltered state"""

        self.filterConditions = {"Remove": []}
        self.setFilterFixedString("")
