"""
JobsTableView - View to display/manipulate jobs
"""

# JTV0001

import logging
import io
import csv

from PySide2.QtWidgets import (
    QTableView,
    QAbstractItemView,
    QSizePolicy,
    QMenu,
    QApplication,
    QHeaderView,
)


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class JobsTableView(QTableView):
    """
    JobsTableView:

    Arguments:
        QTableView {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    # Class logging state
    __log = False

    def __init__(self, parent=None, model=None, title=None):
        super(JobsTableView, self).__init__()

        self.parent = parent
        self.model = model
        self.viewTitle = title
        self.__log = None  # Instance logging state None = Class state prevails

        self._initHelper()
        self.setModel(model)
        self.setSortingEnabled(True)

    def _initHelper(self):

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)

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

        return JobsTableView.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def setVisibleColumns(self, columnsToInclude=None):
        """
        Hides columns so that only those specified in the columnsToInclude list are shown

        :param columnsToInclude: list of str, items must be column names as defined in the
            underlying TableModel
        """

        if columnsToInclude is None:
            columnsToInclude = []

        for i, column in enumerate(self.model.sourceModel().columns):
            hide = column not in columnsToInclude
            self.setColumnHidden(i, hide)

    def contextMenuEvent(self, event):
        """Context Menu"""

        row = self.rowAt(event.pos().y())
        totalRows = self.model.rowCount()

        if 0 <= row < totalRows:

            menu = QMenu()

            menu.addAction("Copy")
            menu.addAction("Remove")

            if action := menu.exec_(event.globalPos()):

                result = action.text()

                if result == "Copy":
                    self.copySelection()

                elif result == "Remove":
                    self.model.filterConditions["Remove"].append(row)
                    self.model.setFilterFixedString("")

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
        row = self.model.mapToSource(index).row()
        contextMenu = QMenu(self)
        menuItems = {}

        for item in ["Copy", "Remove"]:  # Build menu first
            menuItems[item] = contextMenu.addAction(item)

        selection = contextMenu.exec_(event.globalPos())  # Identify the selected item

        if selection == menuItems["Copy"]:  # Specify what happens for each item
            self.copySelection()

        elif selection == menuItems["Remove"]:
            self.model.filterConditions["Remove"].append(row)
            self.model.setFilterFixedString("")

    def resizeEvent(self, event):

        # Adjust the size of rows when font changes
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        # Adjust the width of Job Status column is specific to
        # current app
        header = self.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        # width = header.sectionSize(2)
        # header.setSectionResizeMode(2, QHeaderView.Interactive)
        # header.resizeSection(2, width)

        header.setFont(self.parent.font())

        super(JobsTableView, self).resizeEvent(event)

    def copySelection(self):
        """
        This function copies the selected cells in a table view, accounting for filters and rows as
        well as non-continuous selection ranges. The format of copied values can be pasted into
        Excel retaining the original organization.

        Adapted from code provided by ekhumoro on StackOverflow
        """

        selection = self.selectedIndexes()

        if selection:

            rows = [index.row() for index in selection]
            columns = [index.column() for index in selection]
            rowCount = max(rows) - min(rows) + 1
            colCount = max(columns) - min(columns) + 1
            table = [[""] * colCount for _ in range(rowCount)]

            for index in selection:
                row = index.row() - min(rows)
                column = index.column() - min(columns)
                table[row][column] = index.data()

            stream = io.StringIO()
            csv.writer(stream, delimiter="\t").writerows(table)
            QApplication.clipboard().setText(stream.getvalue())