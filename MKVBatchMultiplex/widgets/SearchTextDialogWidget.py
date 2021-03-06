"""
Search records with specified text in the command
"""


from PySide2.QtCore import QObject, Qt, Slot
from PySide2.QtWidgets import QDialog, QDialogButtonBox

from ..ui import Ui_SearchTextDialog


class SearchTextDialogWidget(QDialog):
    """Search for records with the specified text in dialog"""

    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_SearchTextDialog()
        self.ui.setupUi(self)

        self.parent = parent

        self._initUI()
        self._initVars()
        self._initHelper()

    def _initUI(self):
        """
        _initUI declare needed properties usually one time only
        """
        self.btnBoxOk = self.ui.btnBox.button(QDialogButtonBox.Ok)
        self.btnBoxCancel = self.ui.btnBox.button(QDialogButtonBox.Cancel)
        self.database = None
        self.search = Search(self)

    def _initVars(self):
        """
        _initVars set properties values for a reusable class
        """

        if self.ui.leSearchText.text()  == "":
            self.ui.btnSearchText.setEnabled(False)
            self.btnBoxOk.setEnabled(False)
        else:
            self.ui.btnSearchText.setEnabled(True)
            self.btnBoxOk.setEnabled(True)

        self.cursor = None
        self.ui.lblResult.setText("")

    def _initHelper(self):
        """
        _initHelper one time class properties and any special configuration
            setup
        """

        # remove ? help symbol from dialog header
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        #
        # connect to signals
        # `
        self.ui.btnSearchText.clicked.connect(self.search.searchForRecords)
        self.ui.leSearchText.textChanged.connect(self.searchButtonState)

    def retranslateUi(self):
        self.ui.retranslateUi(self)

    def searchText(self, database):
        """
        searchText search for text in the records of the database

        Returns:
            object: sqlite3 database to be searched
        """

        self._initVars()
        self.database = database
        if not database:
            return None

        rc = self.exec_()

        if rc:
            return self.cursor

        return rc

    def searchButtonState(self):

        if self.ui.leSearchText.text() != "":
            self.ui.btnSearchText.setEnabled(True)
            self.ui.lblResult.setText("")
        else:
            self.ui.btnSearchText.setEnabled(False)
            self.btnBoxOk.setEnabled(False)


class Search(QObject):
    """ search for text in records """

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self._initVars()

    def _initVars(self):

        pass

    @Slot(bool)
    def searchForRecords(self, checked=False):
        """
        searchForRecords Search for records that match

        Args:
            checked (bool, optional): May be unused. Defaults to False.
        """

        fullTextExp = self.parent.ui.leSearchText.text()
        msg = ""
        if fullTextExp:
            if self.parent.database:
                self.parent.cursor = self.parent.database.textSearch(fullTextExp)
                if self.parent.cursor:
                    row = self.parent.cursor.fetchone()
                    if row:
                        self.parent.btnBoxOk.setEnabled(True)
                        # Query again reset cursor and be able to show then
                        # in calling function/method
                        self.parent.cursor = self.parent.database.textSearch(
                            fullTextExp
                        )
                        msg = "Records found."
                    else:
                        msg = "No Records found."
                else:
                    msg = "Nothing found."
                    self.parent.btnBoxOk.setEnabled(False)

        self.parent.ui.lblResult.setText(msg)
