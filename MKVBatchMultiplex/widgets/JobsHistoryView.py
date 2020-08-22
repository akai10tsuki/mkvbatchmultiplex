"""
JobsHistoryView - View to display/manipulate jobs
"""

# JTV0001

import logging
import io
import csv

from PySide2.QtCore import Qt, QPersistentModelIndex, QModelIndex, Slot

from PySide2.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QSizePolicy,
    QMenu,
    QApplication,
    QHeaderView,
)

#from vsutillib.mkv import MKVCommand, MKVCommandParser
from vsutillib.mkv import MKVCommandParser

from ..jobs import JobStatus, JobHistoryKey

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsHistoryView(QTableView):
    """
    JobsHistoryView:

    Arguments:
        QTableView {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    # Class logging state
    __log = False

    def __init__(self, parent=None, proxyModel=None, title=None, log=None):
        super(JobsHistoryView, self).__init__()

        self.__log = None  # Instance logging state None = Class state prevails

        self.parent = parent
        self.proxyModel = proxyModel
        self.viewTitle = title
        self.log = log

        self.setModel(proxyModel)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        # self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clicked.connect(self.clickClear)
        self._initHelper()

    def _initHelper(self):

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)
        self.setAcceptDrops(True)

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:
                returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """

        if self.__log is not None:
            return self.__log

        return JobsHistoryView.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""

        if isinstance(value, bool) or value is None:
            self.__log = value

    def setVisibleColumns(self, columnsToInclude=None):
        """
        Hides columns so that only those specified in the columnsToInclude list
        are shown

        :param columnsToInclude: list of str, items must be column names as
            defined in the underlying TableModel
        """

        if columnsToInclude is None:
            columnsToInclude = []

        for i, column in enumerate(self.proxyModel.sourceModel().columns):
            hide = column not in columnsToInclude
            self.setColumnHidden(i, hide)

    def contextMenuEvent(self, event):
        """Context Menu"""

        row = self.rowAt(event.pos().y())
        totalRows = self.proxyModel.rowCount()

        if 0 <= row < totalRows:

            menu = QMenu()
            menu.setFont(self.parent.font())
            menu.addAction("Copy")
            menu.addAction("Remove")
            menu.addAction("Delete")

            if action := menu.exec_(event.globalPos()):
                result = action.text()

                if result == "Copy":
                    self.copyCommand()
                if result == "Delete":
                    self.deleteSelectedRows()
                elif result == "Remove":
                    self.proxyModel.filterConditions["Remove"].append(row)
                    self.proxyModel.setFilterFixedString("")

    def contextMenuEventOriginal(self, event):
        """
        Sets up the menu to show when a cell is right-clicked. This example includes a 'Remove'
        option which, when selected, adds the clicked row to a list of rows to be filtered out
        and calls the filtering method for the proxy model to hide the row. Different context
        menus can be set up for different columns if desired by reading the column number from
        the index, cross-checking it with the columns list in the source model, and building
        the menu items under if else statements (e.g. if column_name == "Column A").

        :param event: right click event, used to access the index (row/column) which was clicked
        """

        index = self.indexAt(event.pos())
        row = self.proxyModel.mapToSource(index).row()
        contextMenu = QMenu(self)
        menuItems = {}

        for item in ["Copy", "Delete", "Remove"]:  # Build menu first
            menuItems[item] = contextMenu.addAction(item)

        selection = contextMenu.exec_(event.globalPos())  # Identify the selected item

        if selection == menuItems["Copy"]:  # Specify what happens for each item
            self.copySelection()
        elif selection == menuItems["Remove"]:
            self.proxyModel.filterConditions["Remove"].append(row)
            self.proxyModel.setFilterFixedString("")
        elif selection == menuItems["Delete"]:
            self.deleteSelectedRows()

    def resizeEvent(self, event):

        # Adjust the size of rows when font changes
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        # Adjust the width of Job Status column is specific to
        # current app

        header = self.horizontalHeader()
        # header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        width = header.sectionSize(2)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.resizeSection(2, width)
        header.setFont(self.parent.font())

        super(JobsHistoryView, self).resizeEvent(event)

    def copyCommand(self):
        """
        copyCommand copy selected rows
        """

        selection = self.selectedIndexes()

        if selection:
            rows = [index.row() for index in selection]
            columns = [index.column() for index in selection]
            if len(rows) == 4:
                model = self.proxyModel.sourceModel()
                row = rows[3]
                column = columns[3]
                command = model.dataset.data[row][column].cell
                QApplication.clipboard().setText(command)

    def supportedDropActions(self):  # pylint: disable=no-self-use

        return Qt.CopyAction | Qt.MoveAction

    def deleteSelectedRows(self):
        """
        deleteSelectedRows delete selected rows
        """

        model = self.proxyModel.sourceModel()

        proxyIndexList = []
        for i in self.selectionModel().selectedRows():
            index = QPersistentModelIndex(i)
            proxyIndexList.append(index)

        for index in proxyIndexList:
            modelIndex = self.proxyModel.mapToSource(index)
            row = modelIndex.row()
            rowid = model.dataset.data[row][JobHistoryKey.ID].obj
            rowid0 = model.dataset[row, JobHistoryKey.ID]
            print(f"From History View - model call row {row} data row ID {rowid} ID {rowid0}")
            model.removeRows(row, 1)

    def rowsAboutToBeRemoved(self, parent, first, last):
        pass

    @Slot(object)
    def clickClear(self, index):
        pass
