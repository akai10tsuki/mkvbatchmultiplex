"""
JobsHistoryView - View to display/manipulate jobs
"""

# JTV0001

import logging

# import io
# import csv

from PySide2.QtCore import Qt, QPersistentModelIndex, Signal, Slot

from PySide2.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QSizePolicy,
    QMenu,
    QApplication,
    QHeaderView,
)

# from vsutillib.mkv import MKVCommand, MKVCommandParser
# from vsutillib.mkv import MKVCommandParser

from .. import config
from ..jobs import JobHistoryKey, SqlJobsTable, removeFromDb
from ..utils import yesNoDialog

from ..dataset import TableData, tableHistoryHeaders
from ..models import TableModel, TableProxyModel

from .JobsViewHelpers import removeJob

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

    # Signals
    rowCountChangedSignal = Signal(int, int)
    clickedOutsideRowsSignal = Signal(int, int)

    def __init__(self, parent=None, title=None, log=None):
        super(JobsHistoryView, self).__init__()

        self.__log = None  # Instance logging state None = Class state prevails

        self.parent = parent
        # self.proxyModel = proxyModel
        self.viewTitle = title
        self.log = log

        headers = tableHistoryHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = TableModel(self, tableData=self.tableData)
        self.proxyModel = TableProxyModel(self.model)

        self.setModel(self.proxyModel)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        # self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
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
            menu.addAction(_("Copy to command"))
            # menu.addAction(_("Remove"))
            menu.addAction(_("Delete"))

            if action := menu.exec_(event.globalPos()):
                result = action.text()

                if result == _("Copy to command"):
                    self.copyCommand()
                if result == _("Delete"):
                    self.deleteSelectedRows()
                elif result == _("Remove"):
                    self.removeSelection()
                    # self.proxyModel.filterConditions["Remove"].append(row)
                    # self.proxyModel.setFilterFixedString("")

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

    def mousePressEvent(self, event):

        super().mousePressEvent(event)

        row = self.rowAt(event.pos().y())
        # print(f"Selected Rows View clicked row = {row}")

        if row < 0:
            # generate signal when clicked outside the rows
            # this action would deselect all rows but is slow
            # compared the trigger of the signal which make it
            # fail on buttonState this arguments are set to
            # recognize the event and attend the event as if
            # no rows are selected un-elegant hack
            # print("Clicked outside.....")
            self.clickedOutsideRowsSignal.emit(-1, 0)

    def selectedRowsCount(self):

        selectedRows = len(self.selectionModel().selectedRows())

        return selectedRows

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

        super().resizeEvent(event)

    def clearSelection(self):
        print("clearSelection")
        super().clearSelection()

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
                command = model.dataset.data[row][column].cell.strip()
                job = model.dataset.data[row][JobHistoryKey.Status].obj
                QApplication.clipboard().setText(command)
                self.parent.pasteCommandSignal.emit(command)
                if job is not None:
                    self.parent.updateAlgorithmSignal.emit(job.algorithm)


    def supportedDropActions(self):  # pylint: disable=no-self-use

        return Qt.CopyAction | Qt.MoveAction

    def deleteSelectedRows(self):
        """
        deleteSelectedRows delete selected rows
        """

        bAnswer = yesNoDelete(self, "Permanently delete selected rows", "Delete rows")

        if bAnswer:

            jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))

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
                removeFromDb(jobsDB, rowid, rowid0)
                model.removeRows(row, 1)

            jobsDB.close()

    def removeSelection(self):
        """
        removeSelection filter out selected rows
        """

        selection = self.selectedIndexes()
        remove = None
        removeItems = []

        if selection:
            remove = removeJob(self, None)
            if not remove:
                return
            # Get all map indexes before table update
            # When one element is removed the map won't work
            for index in selection:
                modelIndex = self.proxyModel.mapToSource(index)
                row = modelIndex.row()
                removeItems.append(row)

            for row in removeItems:
                self.proxyModel.filterConditions["Remove"].append(row)
                self.proxyModel.setFilterFixedString("")

    def rowCountChanged(self, oldCount, newCount):
        self.rowCountChangedSignal.emit(oldCount, newCount)


def yesNoDelete(parent, pMsg, pTitle):
    """Confirm deletetion"""

    language = config.data.get(config.ConfigKey.Language)
    bAnswer = False
    title = _(pTitle)
    msg = "¿" if language == "es" else ""
    msg += _(pMsg) + "?"
    bAnswer = yesNoDialog(parent, msg, title)

    return bAnswer
