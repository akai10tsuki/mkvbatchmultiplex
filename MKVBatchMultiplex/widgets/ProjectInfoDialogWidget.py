""" Project Information """

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

#from vsutillib.pyqt import centerWidget

#from .. import config
from ..ui import Ui_ProjectInfoDialog


class ProjectInfoDialogWidget(QDialog):
    """
    ProjectInfoDialogWidget change configuration parameters
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_ProjectInfoDialog()
        self.ui.setupUi(self)

        self.__parent = None
        self.parent = parent

        # remove ? help symbol from dialog header
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._initUI()

    def _initUI(self):

        self.__name = None
        self.__info = None

    @property
    def info(self):
        return self.__name, self.__info

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            self.__name = value
            self.ui.leName.clear()
            self.ui.leName.setText(self.__name)

    @property
    def description(self):
        return self.__info

    @description.setter
    def description(self, value):
        if isinstance(value, str):
            self.__info = value
            self.ui.teDescription.clear()
            self.ui.teDescription.insertPlainText(self.__info)

    def getProjectInfo(self):
        """Show dialog to set preferences"""

        self._initUI()

        rc = self.exec()
        if rc:
            self.__name = self.ui.leName.text()
            self.__info = self.ui.teDescription.toPlainText()

        return rc
