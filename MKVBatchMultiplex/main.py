"""
MKVBatchMultiplex entry point
"""

#MAI0004

import logging
import os
import platform
import sys

from collections import deque
from pathlib import Path

from typing import Optional

from PySide6.QtCore import (
    QByteArray,
    QEvent,
    QFile,
    QFileInfo,
    QSaveFile,
    QSettings,
    QTextStream,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QKeySequence,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStatusBar,
    QStyle,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from vsutillib.pyside6 import (
    centerWidget,
    checkColor,
    darkPalette,
    QActionWidget,
    QActivityIndicator,
    QMenuWidget,
    QOutputTextWidget,
    TabWidget,
    VerticalLine,
)

from . import config
from .utils import (
    configLanguage,
    icons,
    SetLocale,
    Text,
    UiSetLocale,
    yesNoDialog,
)
from .widgets import (
    CommandWidget,
    PreferencesDialogWidget,
)


class MainWindow(QMainWindow):
    """ Main window of application """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.parent = parent

        # Language setup has to be early so _() is defined
        self.setInterfaceLocale = SetLocale()
        self.uiSetLocale = UiSetLocale(self)
        configLanguage(self)

        self._initVars()
        self._initHelper()
        self._initUI()

        self.setWindowTitle(Text.txt0001)
        self.setWindowIcon(QIcon(QPixmap(":/images/Itsue256x256.png")))

        #self._text_edit = QTextEdit()
        #self.setCentralWidget(self._text_edit)

        self.createActions()
        self.createMenus()
        self.createToolbars()
        self.createStatusbar()

        self.configuration(action=config.Action.Restore)

        self.setLanguage()

        self.setUnifiedTitleAndToolBarOnMac(True)
        self.show()

    # region Initialization

    def _initVars(self) -> None:

        #
        # Where am I running from
        #

        # if getattr(sys, "frozen", False):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__))
        else:
            self.appDirectory = Path(os.path.realpath(__file__))

        self.setPreferences = PreferencesDialogWidget(self)
        self.setInterfaceLocale.addSlot(self.setPreferences.retranslateUi)
        self.activitySpinner = QActivityIndicator(self)
        
        self.commandWidget = CommandWidget(self)

        self.controlQueue = deque()
        self.tabs = TabWidget(self)

    def _initHelper(self) -> None:
        # work in progress spin
        self.activitySpinner.displayedWhenStopped = True
        self.activitySpinner.color = checkColor(
            QColor(42, 130, 218),
            config.data.get(config.ConfigKey.DarkMode)
        )
        self.activitySpinner.delay = 60

        self.setInterfaceLocale.addSlot(self.commandWidget.setLanguage)

        # Tabs
        tabsList = []
        tabsList.append(
            [
                self.commandWidget,
                _(Text.txt0133),
                _(Text.txt0148),
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

    # endregion

    # region events

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

    #endregion

    # region interface

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
        exitIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
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

        self.actAbout = QActionWidget(
            Text.txt0063,
            self,
            statusTip=Text.txt0065,
            triggered=self.about
        )

        self.actAboutQt = QActionWidget(
            Text.txt0064,
            self,
            statusTip=Text.txt0066,
            triggered=QApplication.aboutQt
        )

        self.setInterfaceLocale.addSlot(self.actPreferences.setLanguage)
        self.setInterfaceLocale.addSlot(self.actExit.setLanguage)
        self.setInterfaceLocale.addSlot(self.actAbort.setLanguage)
        self.setInterfaceLocale.addSlot(self.actAbout.setLanguage)
        self.setInterfaceLocale.addSlot(self.actAboutQt.setLanguage)

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
        self.setInterfaceLocale.addSlot(self.fileMenu.setLanguage)

        #
        # Help menu
        #
        self.helpMenu = QMenuWidget(Text.txt0060)
        self.helpMenu.addAction(self.actAbout)
        self.helpMenu.addAction(self.actAboutQt)

        menuBar.addMenu(self.helpMenu)
        self.setInterfaceLocale.addSlot(self.helpMenu.setLanguage)

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

    # endregion

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

    def setLanguage(self, language: Optional[str] = None) -> None:
        """
        Set application language the scheme permits runtime changes

        Keyword Arguments:
            language (str) -- language selected (default: {"en"})
        """

        configLanguage(self, language)

        self.setWindowTitle(_(Text.txt0001))

        self.setInterfaceLocale.emitSignal()

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

    logging.warning(f"MAI0004: Application Aborted")
    QApplication.exit(1)  # pylint: disable=E1101


def mainApp():
    """Main function"""

    app = QApplication(sys.argv)
    config.init(app=app)

    # Palette will change on macOS according to current theme
    # will create a poor mans dark theme for windows
    if platform.system() == "Windows":
        # pass
        darkPalette(app)
        config.data.set(config.ConfigKey.DarkMode, True)
        QOutputTextWidget.isDarkMode = True
    #mw = MainWindow()
    #mw.show()
    MainWindow()
    app.exec()

    config.close()

# This if for Pylance _() is not defined


def _(dummy):
    return dummy


del _


if __name__ == '__main__':
    sys.exit(mainApp())
