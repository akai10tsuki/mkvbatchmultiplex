
r"""
MKVBatchMultiplex entry point
"""

import gettext
import sys

from typing import Optional

from PySide6.QtCore import (
    QByteArray,
    QFile,
    QFileInfo,
    QSaveFile,
    QSettings,
    QTextStream,
    Qt,
    Signal,
    Slot
)

from PySide6.QtCore import QEvent
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QWidget
)

from . import config
from . import application_rc
from .utils import (
    configLanguage,
    Text,
    yesNoDialog
)


class MainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent

        # Language setup
        configLanguage(self)

        self.setWindowTitle(_(Text.txt0001))

        #self._cur_file = ''

        self._text_edit = QTextEdit()
        self.setCentralWidget(self._text_edit)

        self.createActions()
        self.create_menus()
        self.create_tool_bars()
        self.create_status_bar()

        self.read_settings()

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.show()

    def closeEvent(self, event: QEvent):

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False
        title = _(Text.txt0080)
        leadQuestionMark = "¿" if language == "es" else ""
        msg = leadQuestionMark + _(Text.txt0081) + "?"

        bAnswer = yesNoDialog(self, msg, title)
        if bAnswer:
            #self.configuration(action=config.Action.Save)
            event.accept()
        else:
            event.ignore()

    def about(self):
        """About"""

        aboutMsg = (f"{config.APPNAME}: {config.VERSION}\n\n"
                    f"{_(Text.txt0002)}: {config.AUTHOR}\n"
                    f"{_(Text.txt0003)}: {config.EMAIL}\n\n"
                    f"{_(Text.txt0004)}:\n{sys.version}    \n")

        QMessageBox.about(self, config.APPNAME, aboutMsg)

    def createActions(self):
        self._exit_act = QAction("E&xit", self, shortcut="Ctrl+Q",
                                 statusTip="Exit the application", triggered=self.close)
        self._about_act = QAction("&About", self,
                                  statusTip="Show the application's About box",
                                  triggered=self.about)

        self._about_qt_act = QAction("About &Qt", self,
                                     statusTip="Show the Qt library's About box",
                                     triggered=qApp.aboutQt)

    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_act)

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_qt_act)

    def create_tool_bars(self):
        self._file_tool_bar = self.addToolBar("File")

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def read_settings(self):
        settings = QSettings('QtProject', 'Application Example')
        geometry = settings.value('geometry', QByteArray())
        if geometry.size():
            self.restoreGeometry(geometry)

    def write_settings(self):
        settings = QSettings('QtProject', 'Application Example')
        settings.setValue('geometry', self.saveGeometry())


def mainApp():
    """Main function"""

    app = QApplication(sys.argv)
    config.init(app=app)

    mw = MainWindow()
    mw.show()
    # MainWindow()
    app.exec()

    config.close()

# This if for Pylance _() is not defined


def _(dummy):
    return dummy


del _


if __name__ == '__main__':
    sys.exit(mainApp())
