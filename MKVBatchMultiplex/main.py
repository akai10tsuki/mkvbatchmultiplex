"""
MKVBatchMultiplex entry point
"""

# MAI0004

# region imports

import ctypes
from ctypes import wintypes

import logging
import os
import platform
import sys
from collections import deque
from pathlib import Path
from typing import Optional

from PySide6.QtCore import (QByteArray, QEvent, QFile, QFileInfo, QSaveFile,
                            QSettings, Qt, QTextStream, Signal, Slot)
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QPixmap
from PySide6.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                               QMenuBar, QMessageBox, QStatusBar, QStyle,
                               QTextEdit, QToolTip, QVBoxLayout, QWidget)
from vsutillib.pyside6 import (DualProgressBar, QActionWidget, QActivityIndicator, QMenuWidget,
                               QOutputTextWidget, QSystemTrayIconWidget,
                               TabWidget, VerticalLine, centerWidget,
                               checkColor, darkPalette)

from . import config
from .dataset import TableData, tableHeaders
from .jobs import JobQueue
from .models import TableProxyModel, JobsTableModel
from .utils import (OutputWindows, Text, Translate, UiSetMessagesCatalog,
                    configMessagesCatalog, icons, yesNoDialog)
from .widgets import (CommandWidget, JobsOutputErrorsWidget, JobsOutputWidget,
                      JobsTableViewWidget, PreferencesDialogWidget)

# endregion imports


class MainWindow(QMainWindow):
    """ Main window of application """

    trayIconMessageSignal = Signal(str, str, object)

    # region Initialization

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent

        self.setWindowIcon(QIcon(QPixmap(":/images/Itsue256x256.png")))

        # Language setup has to be early so _() is defined
        self.translateInterface = Translate()
        self.uiTranslateInterface = UiSetMessagesCatalog(self)
        configMessagesCatalog(self)

        self._initVars()
        self._initHelper()
        self._initUI()

        self.createActions()
        self.createMenus()
        self.createToolbars()
        self.createStatusbar()

        self.configuration(action=config.Action.Restore)

        self.translate()

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.trayIcon.show()
        self.show()

    def _initVars(self) -> None:

        #
        # Where am I running from
        #

        self.log = False

        # if getattr(sys, "frozen", False):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__))
        else:
            self.appDirectory = Path(os.path.realpath(__file__))

        self.trayIcon = QSystemTrayIconWidget(self, self.windowIcon())

        self.setPreferences = PreferencesDialogWidget(self)
        self.translateInterface.addSlot(self.setPreferences.retranslateUi)
        self.activitySpinner = QActivityIndicator(self)

        self.controlQueue = deque()
        self.commandEntry = CommandWidget(self)
        self.jobsOutput = JobsOutputWidget(self)
        self.errorOutput = JobsOutputErrorsWidget(self)

        self.jobsQueue = JobQueue(self, controlQueue=self.controlQueue)
        # Model view
        headers = tableHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.model = JobsTableModel(self.tableData, self.jobsQueue)
        self.proxyModel = TableProxyModel(self.model)

        # Widgets for tabs
        self.jobsTableViewWidget = JobsTableViewWidget(
            self, self.proxyModel, self.controlQueue, _(Text.txt0130)
        )

        # self.output = None
        # Set output to contain output windows objects
        self.output = OutputWindows(
            self.commandEntry.outputWindow,
            self.jobsOutput,
            self.errorOutput,
        )

        self.tabs = TabWidget(self)

    def _initHelper(self) -> None:
        # work in progress spin
        self.activitySpinner.displayedWhenStopped = True
        self.activitySpinner.color = checkColor(
            QColor(42, 130, 218),
            config.data.get(config.ConfigKey.DarkMode)
        )
        self.activitySpinner.delay = 60

        self.translateInterface.addSlot(self.commandEntry.translate)

        self.commandEntry.output = self.output
        self.jobsQueue.proxyModel = self.proxyModel

        self.jobsOutput.setReadOnly(True)
        self.errorOutput.setReadOnly(True)

        # Tabs
        tabsList = []
        tabsList.append(
            [
                self.commandEntry,
                _(Text.txt0133),
                _(Text.txt0148),
            ]
        )
        tabsList.append(
            [
                self.jobsTableViewWidget,
                _(Text.txt0140),
                _(Text.txt0144),
            ]
        )
        tabsList.append(
            [
                self.jobsOutput,
                _(Text.txt0141),
                _(Text.txt0145),
            ]
        )
        tabsList.append(
            [
                self.errorOutput,
                _(Text.txt0152),
                _(Text.txt0146),
            ]
        )

        self.tabs.addTabs(tabsList)

    def _initUI(self):

        # Create Widgets
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # endregion Initialization

    # region Events

    def closeEvent(self, event: QEvent) -> None:

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False
        title = _(Text.txt0080)
        leadQuestionMark = "¿" if language == "es" else ""
        msg = leadQuestionMark + _(Text.txt0081) + "?"

        bAnswer = yesNoDialog(self, msg, title)
        if bAnswer:
            self.configuration(action=config.Action.Save)
            event.accept()
        else:
            event.ignore()

    # endregion Events

    # region Overrides

    def setVisible(self, visible):
        """ Override setVisible """

        self.trayIcon.setMenuEnabled(visible)
        super().setVisible(visible)

    # endregion Overrides

    # region Interface

    def createActions(self) -> None:
        """Actions to use in menu interface"""

        self.actPreferences = QActionWidget(
            Text.txt0050,
            self,
            shortcut=Text.txt0026,
            statusTip=Text.txt0051,
            triggered=self.setPreferences.getPreferences
        )

        icon = QIcon(QPixmap(":/images/exit.png"))
        # exitIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        self.actExit = QActionWidget(
            icon,
            Text.txt0021,
            self,
            shortcut=Text.txt0022,
            statusTip=Text.txt0023,
            triggered=self.close
        )

        self.actAbort = QActionWidget(
            Text.txt0024,
            self,
            statusTip=Text.txt0025
        )
        self.actAbort.triggered.connect(abort)

        # No status tip statusTip=Text.txt0065,
        self.actAbout = QActionWidget(
            Text.txt0063,
            self,
            triggered=self.about
        )

        # No status statusTip=Text.txt0066,
        self.actAboutQt = QActionWidget(
            Text.txt0064,
            self,
            triggered=QApplication.aboutQt
        )

        self.translateInterface.addSlot(self.actPreferences.translate)
        self.translateInterface.addSlot(self.actExit.translate)
        self.translateInterface.addSlot(self.actAbort.translate)
        self.translateInterface.addSlot(self.actAbout.translate)
        self.translateInterface.addSlot(self.actAboutQt.translate)

    def createMenus(self) -> None:
        """Create the application menus"""

        menuBar = QMenuBar()

        #
        # File menu
        #
        self.fileMenu = QMenuWidget(Text.txt0020)

        self.fileMenu.addAction(self.actPreferences)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actAbort)

        menuBar.addMenu(self.fileMenu)
        self.translateInterface.addSlot(self.fileMenu.translate)

        #
        # Help menu
        #
        self.helpMenu = QMenuWidget(Text.txt0060)
        self.helpMenu.addAction(self.actAbout)
        self.helpMenu.addAction(self.actAboutQt)

        menuBar.addMenu(self.helpMenu)
        self.translateInterface.addSlot(self.helpMenu.translate)

        # Attach menu
        self.setMenuBar(menuBar)

    def createToolbars(self) -> None:
        self.fileToolbar = self.addToolBar("File")
        self.fileToolbar.addAction(self.actExit)

    def createStatusbar(self) -> None:

        statusBar = QStatusBar()
        statusBar.addPermanentWidget(VerticalLine())
        statusBar.addPermanentWidget(self.activitySpinner)

        self.setStatusBar(statusBar)

    # endregion Interface

    # region Configuration

    def configuration(self, action: str) -> None:
        """
        Read/Write configuration
        """

        defaultFont = QFont()
        defaultFont.fromString(config.data.get(config.ConfigKey.SystemFont))
        defaultFont.setPointSize(14)
        bLogging = False

        if action == config.Action.Reset:
            self.setFont(defaultFont)
            self.setAppFont(defaultFont)

            self.enableLogging(bLogging)

            self.setGeometry(0, 0, 1280, 70)
            centerWidget(self)
        elif action == config.Action.Restore:
            if strFont := config.data.get(config.ConfigKey.Font, defaultFont):
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)
                self.setAppFont(restoreFont)

            if bLogging := config.data.get(config.ConfigKey.Logging):
                self.enableLogging(bLogging)

            if byteGeometry := config.data.get(config.ConfigKey.Geometry):
                self.restoreGeometry(
                    QByteArray.fromBase64(QByteArray(byteGeometry)))
            else:
                self.setGeometry(0, 0, 1280, 720)
                centerWidget(self)
        elif action == config.Action.Save:
            # Update geometry includes position
            base64Geometry = self.saveGeometry().toBase64()
            b = base64Geometry.data()  # b is a bytes string
            config.data.set(config.ConfigKey.Geometry, b)

    def enableLogging(self, state):
        """Activate logging"""

        self.log = state
        msg = "MAI0001: Start Logging." if state else "MAI0002: Stop Logging."
        logging.info(msg)
        config.data.set(config.ConfigKey.Logging, state)

    def translate(self, language: Optional[str] = None) -> None:
        """
        Set application language the scheme permits runtime changes

        Keyword Arguments:
            language (str) -- language selected (default: {"en"})
        """

        configMessagesCatalog(self, language)

        self.setWindowTitle(_(Text.txt0001))

        self.translateInterface.emitSignal()

    def setAppFont(self, font):
        """
        Set font selected as application default font

        Arguments:
            font {QFont} -- font selected by user
        """

        for action in self.menuBar().actions():
            if not action.isSeparator():
                action.setFont(font)

        for action in self.fileMenu.actions():
            if not action.isSeparator():
                action.setFont(font)

        for action in self.helpMenu.actions():
            if not action.isSeparator():
                action.setFont(font)

        QToolTip.setFont(font)
        config.data.set(config.ConfigKey.Font, font.toString())

    # endregion

    def about(self) -> None:
        """About"""

        aboutMsg = (f"{config.APPNAME}: {config.VERSION}\n\n"
                    f"{_(Text.txt0002)}: {config.AUTHOR}\n"
                    f"{_(Text.txt0003)}: {config.EMAIL}\n\n"
                    f"{_(Text.txt0004)}:\n{sys.version}\n\n")

        QMessageBox.about(self, config.APPNAME, aboutMsg)


def abort():
    """Force Quit"""

    logging.warning("MAI0004: Application Aborted")
    QApplication.exit(1)  # pylint: disable=E1101


def mainApp():
    """Main function"""

    app = QApplication(sys.argv)
    config.init(app=app)

    # Palette will change on macOS according to current theme
    if platform.system() == "Windows":
        # will create a poor mans dark theme for windows
        # import ctypes

        darkPalette(app)
        config.data.set(config.ConfigKey.DarkMode, True)
        QOutputTextWidget.isDarkMode = True

        myAppID = "VergaraSoft.MKVBatchMultiplex.mkv.3.0.0"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)

    MainWindow()
    app.exec()

    config.close()


# This if for Pylance _() is not defined
def _(dummy):
    return dummy


del _


if __name__ == '__main__':
    sys.exit(mainApp())
