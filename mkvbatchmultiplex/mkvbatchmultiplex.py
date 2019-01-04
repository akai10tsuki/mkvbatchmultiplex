#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
mkvBatchMultiplex
=================

Program for batch processing mkvmerge commands

The program will take command line argument from mkvtoolnix-gui
from MKVToolNix

Multiplexer->Show command line

It will analyze the command and apply the same multiplex instructions to all
the files in the same directory if more than one file is involved in the
command they must match in numbers.

Develop on Windows

Works on:

    * Tested on ubuntu 18.04

Libraries and programs used:

    python 3.6-3.7
    pymediainfo 2.2.1-3.0
    mediainfo-17.10->18.12
    PySide2 5.12

Target program:
    MKVToolNix - tested with versions v17.0.0-29.0.0
"""

import ast
import logging
import logging.handlers
import sys
import os
import xml
import xml.etree.ElementTree as ET
from pathlib import Path
from queue import Queue
from collections import deque

from PySide2.QtCore import QByteArray, Qt, QThreadPool, Signal
from PySide2.QtGui import QIcon, QFont
from PySide2.QtWidgets import (QAction, QApplication, QDesktopWidget, qApp,
                               QMainWindow, QMessageBox, QToolBar, QVBoxLayout,
                               QWidget, QFontDialog)

import mkvbatchmultiplex.config as config

from .loghandler import QthLogRotateHandler
from .widgets import (DualProgressBar, MKVFormWidget, MKVTabsWidget, FormatLabel,
                      MKVOutputWidget, MKVJobsTableWidget)
from .jobs import JobQueue, JobStatus
from .configurationsettings import ConfigurationSettings


class MKVMultiplexApp(QMainWindow): # pylint: disable=R0902
    """Main window of application"""

    log = False
    raiseErrors = False
    outputMainSignal = Signal(str, dict)
    outputQueue = Signal(str, dict)
    outputError = Signal(str, dict)
    addJob = Signal(int, str)
    setJobStatus = Signal(int, str)

    def __init__(self, parent=None):
        super(MKVMultiplexApp, self).__init__(parent)

        self.workQueue = deque()
        self.ctrlQueue = Queue()
        self.threadpool = QThreadPool()
        self.jobs = JobQueue(self.workQueue)
        self.config = ConfigurationSettings()
        self.actEnableLogging = None

        cwd = Path(os.path.realpath(__file__))

        self.setWindowTitle("MKVMERGE: Batch Multiplex")
        self.setWindowIcon(QIcon(str(cwd.parent) + "/images/mkvBatchMultiplex.png"))

        self._initMenu(cwd)
        self._initHelper()

        # Read configuration elements
        self.configuration()
        self.restoreConfig()

    def _initHelper(self):

        # Create Widgets
        self.formWidget = MKVFormWidget(self, self.threadpool, self.jobs, self.ctrlQueue, log=True)
        self.outputQueueWidget = MKVOutputWidget(self)
        self.outputErrorWidget = MKVOutputWidget(self)
        self.jobsWidget = MKVJobsTableWidget(self, self.ctrlQueue)

        # Connect signals to print in outputWidgets and update jobsWidget
        self.jobs.setOutputSignal(
            self.outputQueueWidget.makeConnection,
            self.outputErrorWidget.makeConnection,
            self.jobsWidget.makeConnection0,
            self.jobsWidget.makeConnection1,
            self.clearOutput
        )

        # Connect to signal when a row is clicked on jobsWidget job output
        # will update in outputWidgets
        self.jobs.makeConnection(self.jobsWidget.showJobOutput)
        self.jobs.connectToStatus(self.jobsWidget.jobsTable.updateJobStatus)

        # Create tabs and insert Widgets
        self.tabsWidget = MKVTabsWidget(
            self,
            self.formWidget,
            self.jobsWidget,
            self.outputQueueWidget,
            self.outputErrorWidget
        )

        self.tabs = self.tabsWidget.tabs
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabsWidget)
        self.setCentralWidget(widget)

    def _initMenu(self, cwd):

        menuBar = self.menuBar()

        actExit = QAction(QIcon(str(cwd.parent) + "/images/cross-circle.png"), "&Exit", self)
        actExit.setShortcut("Ctrl+E")
        actExit.setStatusTip("Exit application")
        actExit.triggered.connect(self.close)

        actAbort = QAction("Abort", self)
        actAbort.setStatusTip("Force exit")
        actAbort.triggered.connect(abort)

        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(actExit)
        fileMenu.addAction(actAbort)

        self.actEnableLogging = QAction("Enable logging", self, checkable=True)
        self.actEnableLogging.setStatusTip(
            "Enable session logging in ~/.mkvBatchMultiplex/mkvBatchMultiplex.log"
        )
        self.actEnableLogging.triggered.connect(self.enableLogging)

        actSelectFont = QAction("Font", self)
        actSelectFont.setStatusTip("")
        actSelectFont.triggered.connect(self.selectFont)

        actRestoreDefaults = QAction("Restore Defaults", self)
        actRestoreDefaults.triggered.connect(self.restoreDefaults)

        settingsMenu = menuBar.addMenu("&Settings")
        settingsMenu.addAction(self.actEnableLogging)
        settingsMenu.addAction(actSelectFont)
        settingsMenu.addAction(actRestoreDefaults)

        tb = QToolBar("Exit", self)
        tb.addAction(actExit)
        self.addToolBar(tb)

        self.progressbar = DualProgressBar(align=Qt.Horizontal)
        self.jobsLabel = FormatLabel(
            "Job(s): {0:3d} Current: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}",
            init=[0, 0, 0, 0, 0]
        )

        statusBar = self.statusBar()
        statusBar.addPermanentWidget(self.jobsLabel)
        statusBar.addPermanentWidget(self.progressbar)

    def clearOutput(self):
        """Clear output for JobQueue"""

        self.outputQueueWidget.clear()
        self.outputErrorWidget.clear()

    def closeEvent(self, event):
        """
        Save window state before exit
        m = QMessageBox(self)
        m.setText("Are you sure you want to exit?")
        m.setIcon(QMessageBox.Question)
        m.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        m.setDefaultButton(QMessageBox.Yes)
        result = m.exec_()
        """

        self.formWidget.teOutputWindow.makeConnection(self.outputMainSignal)
        jobsStatus = self.jobs.jobsStatus()

        if jobsStatus == JobStatus.Aborted:

            event.accept()

        else:

            if jobsStatus == JobStatus.Running:

                result = QMessageBox.warning(
                    self,
                    "Confirm Abort...",
                    "Jobs running are you sure you want to stop them?",
                    QMessageBox.Yes | QMessageBox.No
                )

            else:

                result = QMessageBox.question(
                    self,
                    "Confirm Exit...",
                    "Are you sure you want to exit?",
                    QMessageBox.Yes | QMessageBox.No
                )

            if result == QMessageBox.Yes:
                self.configuration(save=True)

                if jobsStatus == JobStatus.Running:
                    self.outputMainSignal.emit(
                        "\nJobs running aborting jobs...\n\n",
                        {'color': Qt.blue}
                    )
                    self.ctrlQueue.put(JobStatus.Abort)
                    event.ignore()

                else:
                    event.accept()
            else:
                event.ignore()

    def enableLogging(self, state):
        """Activate logging"""
        if state:
            self.log = True
            logging.info("Start logging.")
        else:
            self.log = False
            logging.info("Stop logging.")

    def selectFont(self):
        """Select Font"""

        font = self.font()

        fontDialog = QFontDialog()
        centerWidgets(fontDialog, self)

        valid, font = fontDialog.getFont(font)

        if valid:
            self.setFont(font)

    def configuration(self, save=False):
        """Read and write configuration"""
        configFile = Path(Path.home(), ".mkvBatchMultiplex/config-pyside2.xml")
        xmlFile = str(configFile)

        if save:

            self.config.set(
                'logging', self.actEnableLogging.isChecked()
            )

            base64Geometry = self.saveGeometry().toBase64()

            s = str(base64Geometry)
            b = ast.literal_eval(s)

            self.config.set(
                'geometry', b
            )

            font = self.font()

            self.config.set(
                'font', font.toString()
            )

            root = ET.Element("VergaraSoft")
            root = self.config.toXML(root)
            tree = ET.ElementTree(root)
            tree.write(xmlFile)

        else:

            if configFile.is_file():
                try:
                    tree = ET.ElementTree(file=xmlFile)
                    root = tree.getroot()
                    self.config.fromXML(root)
                except NameError:
                    logging.info("MW0002: Bad configuration definition file.")
                except xml.etree.ElementTree.ParseError:
                    logging.info("MW0001: Bad or corrupt configuration file.")
            else:
                configFile.touch(exist_ok=True)

    def restoreConfig(self, resetDefaults=False):
        """Restore configuration if any"""

        defaultFont = QFont("Segoe UI", 9)
        bLogging = False

        if resetDefaults:
            self.setFont(defaultFont)
            self.actEnableLogging.setChecked(bLogging)
            self.enableLogging(bLogging)
            self.setGeometry(0, 0, 1280, 720)
            self._center()

        else:

            strFont = self.config.get('font')

            if strFont is not None:
                restoreFont = QFont()
                restoreFont.fromString(strFont)
                self.setFont(restoreFont)

            else:
                self.setFont(defaultFont)

            bLogging = self.config.get('logging')

            if bLogging is not None:
                self.actEnableLogging.setChecked(bLogging)
                self.enableLogging(bLogging)

            byteGeometry = self.config.get('geometry')

            if byteGeometry is not None:
                # Test for value read if not continue
                #byte = ast.literal_eval(strGeometry)
                byteGeometry = QByteArray(byteGeometry)

                self.restoreGeometry(QByteArray.fromBase64(byteGeometry))
            else:

                self.setGeometry(0, 0, 1280, 720)
                centerWidgets(self)

                #self._center()

    def restoreDefaults(self):
        """restore defaults settings"""

        result = QMessageBox.question(
            self,
            "Confirm Restore...",
            "Restore default settings ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self.restoreConfig(resetDefaults=True)


def centerWidgets(widget, parent=None):
    """center widget based on parent or screen geometry"""

    if parent is None:
        parent = widget.parentWidget()

    if parent:
        widget.move(parent.frameGeometry().center() - widget.frameGeometry().center())

    else:
        widget.move(QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center())

def abort():
    """Force Quit"""

    qApp.quit()     # pylint: disable=E1101

def setupLogging():
    """Configure log"""

    filesPath = Path(Path.home(), ".mkvBatchMultiplex")
    filesPath.mkdir(parents=True, exist_ok=True)

    logFile = Path(Path.home(), ".mkvBatchMultiplex/mkvBatchMultiplex.log")
    logging.getLogger('').setLevel(logging.DEBUG)

    loghandler = QthLogRotateHandler(logFile, backupCount=10)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s %(message)s"
    )

    loghandler.setFormatter(formatter)

    logging.getLogger('').addHandler(loghandler)

def mainApp():
    """Main"""

    setupLogging()

    logging.info("App Start.")
    logging.info("Python: %s", sys.version)
    logging.info("mkvbatchmultiplex-%s", config.VERSION)
    app = QApplication(sys.argv)
    win = MKVMultiplexApp()
    win.show()
    app.exec_()
    logging.info("App End.")

if __name__ == "__main__":
    sys.exit(mainApp())
