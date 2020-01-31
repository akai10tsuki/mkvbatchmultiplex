#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
JobsTable


"""

import gettext
import logging
import os
import platform
import sys
import threading
import webbrowser

from pathlib import Path

from PySide2.QtCore import QByteArray, Slot
from PySide2.QtGui import QIcon, QFont, Qt
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    qApp,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    QFontDialog,
    QToolTip,
    QStyle,
)

from vsutillib.pyqt import (
    centerWidgets,
    darkPalette,
    DualProgressBar,
    FormatLabel,
    OutputTextWidget,
    QActionWidget,
    QMenuWidget,
)

from . import config
from .dataset import TableData, tableHeaders
from .jobs import JobQueue
from .models import TableProxyModel, JobsTableModel
from .widgets import CommandWidget, JobsTableViewWidget, TabsWidget
from .utils import Text, Progress, yesNoDialog, setLanguageMenus, SetLanguage

DEFAULTFONT = QFont("Segoe UI", 14)


class MainWindow(QMainWindow):  # pylint: disable=R0902
    """Main window of application"""

    log = False

    def __init__(self, parent=None, palette=None):
        super(MainWindow, self).__init__(parent)

        self.actEnableLogging = None
        self.actEN = None
        self.actES = None
        self.languageMenu = None
        self.jobQueue = JobQueue(self)
        self.defaultPalette = palette
        self.widgetSetLanguage = SetLanguage()

        #
        # Where am I running from
        #
        if getattr(sys, "frozen", False):
            # Running in a pyinstaller bundle
            self.appDirectory = Path(os.path.dirname(__file__))
        else:
            self.appDirectory = Path(os.path.realpath(__file__))

        self.setWindowTitle(config.APPNAME + ": " + config.DESCRIPTION)
        self.setWindowIcon(QIcon(str(self.appDirectory.parent) + "/images/Itsue.png"))

        # Setup User Interface
        self._initMenu()
        self._initControls()
        self._initUI()
        self._initHelper()

        # Restore configuration elements
        self.configuration(action=config.Action.Restore)
        self.setLanguage()

    def _initControls(self):

        headers = tableHeaders()
        self.tableData = TableData(headerList=headers, dataList=[])
        self.tableModel = JobsTableModel(self.tableData, self.jobQueue)
        self.proxyModel = TableProxyModel(self.tableModel)

        self.progress = Progress(self, self.progressBar, self.jobsLabel)

        self.jobQueue.model = self.proxyModel
        self.jobQueue.progress = self.progress

        # Widgets for tabs
        self.tableViewWidget = JobsTableViewWidget(
            self, self.proxyModel, self.jobQueue, self.progress, "Jobs Table"
        )
        self.tableViewWidget.tableView.sortByColumn(0, Qt.AscendingOrder)

        self.comandWidget = CommandWidget(self, self.proxyModel)
        self.jobsOutput = OutputTextWidget(self)
        self.errorOutput = OutputTextWidget(self)

        self.tabs = TabsWidget(
            self,
            self.comandWidget,
            self.tableViewWidget,
            self.jobsOutput,
            self.errorOutput,
            QWidget(),
        )

    def _initHelper(self):
        """
        _initHelper setup signals
        """

        # map output widgets inserTextSignal to local ones
        self.outputMainSignal = self.comandWidget.insertTextSignal
        self.jobsOutputSignal = self.jobsOutput.insertTextSignal
        self.errorOutputSignal = self.jobsOutput.insertTextSignal

        # setup widgets setLanguage to SetLanguage change signal
        self.widgetSetLanguage.addSlot(self.tableViewWidget.setLanguage)
        self.widgetSetLanguage.addSlot(self.comandWidget.setLanguage)
        self.widgetSetLanguage.addSlot(self.tabs.setLanguage)

        # connect to tabs widget tab change Signal
        self.tabs.currentChanged.connect(tabChange)

    def _initUI(self):

        # Create Widgets
        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabs)

        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def _initMenu(self):  # pylint: disable=too-many-statements

        menuBar = self.menuBar()

        # File SubMenu
        fileMenu = QMenuWidget(Text.txt0026)

        closeIcon = self.style().standardIcon(QStyle.SP_DialogCloseButton)

        # Exit application
        actExit = QActionWidget(
            closeIcon, Text.txt0030, self, shortcut=Text.txt0015, tooltip=Text.txt0014,
        )
        actExit.triggered.connect(self.close)

        # Abort
        actAbort = QActionWidget(Text.txt0017, self, tooltip=Text.txt0018)
        actAbort.triggered.connect(abort)

        # Add actions to SubMenu
        fileMenu.addAction(actExit)
        fileMenu.addAction(actAbort)
        menuBar.addMenu(fileMenu)

        # Settings SubMenu
        settingsMenu = QMenuWidget(Text.txt0027)

        # Enable logging
        self.actEnableLogging = QActionWidget(Text.txt0019, self, checkable=True)
        self.actEnableLogging.setStatusTip(Text.txt0020)
        self.actEnableLogging.triggered.connect(self.enableLogging)

        # Font
        actSelectFont = QActionWidget(Text.txt0021, self)
        actSelectFont.setStatusTip(Text.txt0022)
        actSelectFont.triggered.connect(self.selectAppFont)

        # Restore Defaults
        actRestoreDefaults = QActionWidget(Text.txt0023, self)
        actRestoreDefaults.setStatusTip(Text.txt0045)
        actRestoreDefaults.triggered.connect(self.restoreDefaults)

        self.actEN = QActionWidget(
            "English (Inglés)",
            self,
            checkable=True,
            tooltip="Select english language for the interface",
        )
        self.actEN.triggered.connect(lambda: self.setLanguage("en", self.actEN))

        self.actES = QActionWidget(
            "Español (Spanish)",
            self,
            checkable=True,
            tooltip="Seleccione el idioma Español para la interfaz",
        )
        self.actES.triggered.connect(lambda: self.setLanguage("es", self.actES))

        self.languageMenu = QMenuWidget(Text.txt0028)
        self.languageMenu.addAction(self.actEN)
        self.languageMenu.addAction(self.actES)

        # Add items to Settings SubMenu
        settingsMenu.addAction(self.actEnableLogging)
        settingsMenu.addAction(actSelectFont)
        settingsMenu.addSeparator()
        settingsMenu.addMenu(self.languageMenu)
        settingsMenu.addSeparator()
        settingsMenu.addAction(actRestoreDefaults)
        menuBar.addMenu(settingsMenu)

        # Help Menu
        actHelpContents = QActionWidget(Text.txt0044 + "...", self)
        actHelpContents.triggered.connect(lambda: _help(self.appDirectory, 0))

        actHelpUsing = QActionWidget(Text.txt0024, self)
        actHelpUsing.triggered.connect(lambda: _help(self.appDirectory, 1))

        actAbout = QActionWidget(Text.txt0040, self)
        actAbout.triggered.connect(self.about)

        actAboutQt = QActionWidget("About QT", self)
        actAboutQt.triggered.connect(self.aboutQt)

        helpMenu = QMenuWidget(Text.txt0025)
        helpMenu.addAction(actHelpContents)
        helpMenu.addAction(actHelpUsing)
        helpMenu.addSeparator()
        helpMenu.addAction(actAbout)
        helpMenu.addAction(actAboutQt)
        menuBar.addMenu(helpMenu)

        # Init status var

        self.progressBar = DualProgressBar(align=Qt.Horizontal)
        self.jobsLabel = FormatLabel(
            "Job(s): {0:3d} Current: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}",
            init=[0, 0, 0, 0, 0],
        )

        statusBar = self.statusBar()  # pylint: disable=unused-variable
        statusBar.addPermanentWidget(self.jobsLabel)
        statusBar.addPermanentWidget(self.progressBar)


    def enableLogging(self, state):
        """Activate logging"""

        if state:
            self.log = True
            logging.info("Start logging.")
        else:
            self.log = False
            logging.info("Stop logging.")

    def configuration(self, action=None):
        """
        Read and write configuration
        """

        defaultFont = DEFAULTFONT
        bLogging = False

        if action == config.Action.Reset:

            self.setFont(defaultFont)
            self.setAppFont(defaultFont)

            self.actEnableLogging.setChecked(bLogging)
            self.enableLoggin(bLogging)
            self.setGeometry(0, 0, 1280, 720)
            centerWidgets(self)

        elif action == config.Action.Restore:

            if strFont := config.data.get(config.ConfigKey.Font):
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)
                self.setAppFont(restoreFont)
            else:
                self.setFont(defaultFont)
                self.setAppFont(defaultFont)

            if bLogging := config.data.get(config.ConfigKey.Logging):
                self.actEnableLogging.setChecked(bLogging)
                self.enableLoggin(bLogging)

            if byteGeometry := config.data.get(config.ConfigKey.Geometry):
                self.restoreGeometry(QByteArray.fromBase64(QByteArray(byteGeometry)))
            else:
                self.setGeometry(0, 0, 1280, 720)
                centerWidgets(self)

            if tabIndex := config.data.get("Tab"):
                # setting tab to jobs
                self.tabs.setCurrentIndexSignal.emit(tabIndex)

        elif action in (config.Action.Save, config.Action.Update):

            # Update Logging
            config.data.set(config.ConfigKey.Logging, self.actEnableLogging.isChecked())

            # Update current font
            font = self.font()
            config.data.set(config.ConfigKey.Font, font.toString())

            # Update geometry includes position
            base64Geometry = self.saveGeometry().toBase64()
            b = base64Geometry.data()  # b is a bytes string
            config.data.set(config.ConfigKey.Geometry, b)

            if action == config.Action.Save:

                config.data.saveToFile()

    def restoreDefaults(self):
        """
        Override QMainWindow.closeEvent

        Save configuration state before exit
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False

        title = _(Text.txt0083)
        msg = "¿" if language == "es" else ""
        msg += _(Text.txt0084) + "?"

        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.configuration(action=config.Action.Reset)

    def setAppFont(self, font):
        """
        Set font selected as application default font

        Arguments:
            font {QFont} -- font selected by user
        """

        for a in self.menuBar().actions():
            # menus on menubar are QAction classes
            # get the menu

            m = a.menu()
            m.setFont(font)

            for e in m.actions():
                if e.isSeparator():
                    continue
                elif isinstance(e, QActionWidget):
                    # subclass also QAction type but never a menu
                    continue
                elif isinstance(e, QAction):
                    try:
                        i = e.menu()
                        i.setFont(font)
                    except AttributeError:
                        continue

        QToolTip.setFont(font)

    def selectAppFont(self):
        """Select Font"""

        font = self.font()

        fontDialog = QFontDialog()
        centerWidgets(fontDialog, self)

        valid, font = fontDialog.getFont(font)

        if valid:
            self.setFont(font)
            self.setAppFont(font)
            config.data.set(config.ConfigKey.Font, font.toString())

    def setLanguage(self, language=None, menuItem=None):
        """
        Set application language the scheme permits runtime changes

        Keyword Arguments:
            language {str} -- language selected (default: {'es'})
            menuItem {QMenuWidget} -- menu object making the call for
                checkmark update
        """

        if language is None:
            language = config.data.get(config.ConfigKey.Language)

        lang = gettext.translation(
            config.NAME, localedir=str(config.LOCALE), languages=[language]
        )

        lang.install(names=("ngettext",))

        config.data.set(config.ConfigKey.Language, language)

        self.setWindowTitle(Text.txt0001)
        self.jobsLabel.template = _(Text.txt0085)
        self.progressBar.label = _(Text.txt0091) + ':'

        # Set langque main windows
        setLanguageMenus(self.menuBar().actions())

        # Update checkboxes in the select language menu
        if menuItem is not None:
            for a in self.languageMenu.actions():
                a.setChecked(False)
            menuItem.setChecked(True)
        else:
            if language == "es":
                self.actEN.setChecked(False)
                self.actES.setChecked(True)
            else:
                self.actES.setChecked(False)
                self.actEN.setChecked(True)

        # Update language on other window widgets
        self.widgetSetLanguage.emitSignal()

    def closeEvent(self, event):
        """
        Override QMainWindow.closeEvent

        Save configuration state before exit
        """

        language = config.data.get(config.ConfigKey.Language)
        bAnswer = False

        title = _(Text.txt0080)

        leadQuestionMark = "¿" if language == "es" else ""

        if threading.activeCount() > 1:
            msg = _(Text.txt0089) + ". " + leadQuestionMark + _(Text.txt0090) + "?"
        else:
            msg = leadQuestionMark + _(Text.txt0081) + "?"

        bAnswer = yesNoDialog(self, msg, title)

        if bAnswer:
            self.configuration(action=config.Action.Save)
            event.accept()
        else:
            event.ignore()

    def about(self):
        """About"""
        aboutMsg = config.APPNAME + ": {}\n\n"
        aboutMsg += _(Text.txt0002) + ": {}\n"
        aboutMsg += _(Text.txt0003) + ": {}\n\n"
        aboutMsg += _(Text.txt0004) + ":\n{}\n"

        aboutMsg = aboutMsg.format(
            config.VERSION, config.AUTHOR, config.EMAIL, sys.version
        )
        QMessageBox.about(self, config.APPNAME, aboutMsg)

    def aboutQt(self):
        """About QT"""

        QMessageBox.aboutQt(self, config.APPNAME)


@Slot(int)
def tabChange(index):
    """
    tabChange take action when the tab change for save current tab index

    Args:
        index (int): index of current tab
    """

    config.data.set("Tab", index)


def _help(pth, index=0):
    """open web RTD page"""

    if index == 1:
        htmlPath = "file:///" + str(pth.parent) + "/html/using.html"
    else:
        htmlPath = "file:///" + str(pth.parent) + "/html/index.html"

    webbrowser.open(htmlPath, new=2, autoraise=True)


def abort():
    """Force Quit"""

    qApp.quit()  # pylint: disable=E1101


def mainApp():
    """Main"""

    config.init()

    # PySide2 app
    app = QApplication(sys.argv)

    # Palette will change on macOS according to current theme
    # will create a poor mans dark theme for windows
    if platform.system() == "Windows":

        # Force the style to be the same on all OSs:
        app.setStyle("Fusion")
        app.setPalette(darkPalette())

    win = MainWindow()
    win.show()
    app.exec_()

    config.close()


if __name__ == "__main__":
    sys.exit(mainApp())
