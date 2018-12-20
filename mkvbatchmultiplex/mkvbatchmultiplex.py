#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
mkvBatchMultiplex:
Program for batch processing mkvmerge commands

The program will take command line argument from mkvtoolnix-gui

Multiplexer->Show command line

Works with either Windows (cmd.exe) or Linux/unix shells (bash, zsh, etc.)

It will analyze the command and apply the same multiplex instructions to all
the files in the same directory if more than one file is involved in the
command they must match in numbers. That is multiplex video and subtitle:

    13 - video *.avi - video files
    13 - video *.srt - subtitle files

Files of the same type involved in the same operation must be in different
directories.

    \dir1\video1v1 *.mkv

    \dir2\video1v2 *.mkv

This is because the program will read the source files from the directories
found in the command line and will try to apply the instructions to all
of them.  If the files are of different types that is a video file and a
subtitle file this is not required, the sources are an extension pair.

    \dir1\video1 *.mkv
    \dir1\video1 *.srt


The other condition all different sources must be of the same type.
For example:

    video01.avi->video*.avi, video01.srt->video*.srt

It is been develop on Windows 10 all libraries so far exist for Windows
macOS and Linux. Light testing shows to work for all operating systems
mentioned as of this writing 2018-01-12 ver 0.5.1a1.

Libraries and programs used:

python 3.6-3.7
pymediainfo 2.2.1-3.0
mediainfo-17.10->18.12
PyQt5 5.10.1-5.11.3

Some icons by Yusuke Kamiyamane. Licensed under a Creative Commons Attribution 3.0 License.

Target program
mkvtoolnix-v17.00->29.00

"""

__version__ = "0.5.3a1"
__author__ = "Efrain Vergara"

import base64
import logging
import logging.handlers
import sys
import os
import xml.etree.ElementTree as et
from pathlib import Path
from queue import Queue
from collections import deque

from PyQt5.QtCore import QByteArray, Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QMainWindow, QMessageBox, QToolBar, QVBoxLayout,
                             QWidget)


from .library.loghandler import QthLogRotateHandler
from .library.widgets import (DualProgressBar, MKVFormWidget, MKVTabsWidget,
                             MKVOutputWidget, MKVJobsTableWidget, SpacerWidget)
from .library.pyqtconfig import ConfigManager
from .library.jobs import JobQueue
from .library.widgets import JobStatus


class MKVMultiplexApp(QMainWindow):
    """Main window of application"""

    log = False
    raiseErrors = False
    outputMainSignal = pyqtSignal(str, dict)
    outputQueue = pyqtSignal(str, dict)
    outputError = pyqtSignal(str, dict)
    addJob = pyqtSignal(int, str)
    setJobStatus = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(MKVMultiplexApp, self).__init__(parent)

        self.workQueue = deque()
        self.ctrlQueue = Queue()
        self.threadpool = QThreadPool()
        self.jobs = JobQueue(self.workQueue)

        # Create Widgets
        self.formWidget = MKVFormWidget(self, self.threadpool, self.jobs, self.ctrlQueue)
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
        self.config = ConfigManager()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.tabsWidget)
        self.setCentralWidget(widget)
        self._initMenu()

    def _initMenu(self):

        p = Path(os.path.realpath(__file__))

        actExit = QAction(QIcon(str(p.parent) + "/images/cross-circle.png"), "&Exit", self)
        actExit.setShortcut("Ctrl+E")
        actExit.setStatusTip("Exit application")
        actExit.triggered.connect(self.close)

        toolbar = QToolBar("Exit")
        toolbar.addAction(actExit)
        self.toolbar = self.addToolBar(toolbar)

        self.progressbar = DualProgressBar(align=Qt.Horizontal)
        toolSpacer = SpacerWidget()

        toolbar1 = QToolBar("Progress")
        toolbar1.addWidget(toolSpacer)
        toolbar1.addSeparator()
        toolbar1.addWidget(self.progressbar)
        self.toolbar = self.addToolBar(toolbar1)

        self.statusBar()

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(actExit)

        self.actEnableLogging = QAction("Enable logging", self, checkable=True)
        self.actEnableLogging.setStatusTip(
            "Enable session logging in ~/.mkvBatchMultiplex/mkvBatchMultiplex.log"
        )
        self.actEnableLogging.triggered.connect(self.enableLogging)

        settingsMenu = menuBar.addMenu("&Settings")
        settingsMenu.addAction(self.actEnableLogging)

        # Read configuration elements
        self.configuration()
        self.restoreConfig()

        self.setWindowTitle("MKVMERGE: Batch Multiplex")
        self.setWindowIcon(QIcon(str(p.parent) + "/images/mkvBatchMultiplex.png"))

    def _center(self):
        """Center frame on first run"""

        qR = self.frameGeometry()
        cP = QDesktopWidget().availableGeometry().center()
        qR.moveCenter(cP)
        self.move(qR.topLeft())

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

        result = QMessageBox.question(
            self,
            "Confirm Exit...",
            "Are you sure you want to exit ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self.configuration(save=True)

            tmpNum = self.threadpool.activeThreadCount()

            if tmpNum > 0:
                self.outputMainSignal.emit("\nJobs Running Aborting jobs\n\n", {'color': Qt.blue})
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

    def configuration(self, save=False):
        """Read and write configuration"""
        configFile = Path(Path.home(), ".mkvBatchMultiplex/config.xml")
        xmlFile = str(configFile)

        if save:

            self.config.set(
                'logging', self.actEnableLogging.isChecked()
            )

            byteGeometry = base64.b64encode(self.saveGeometry())
            self.config.set(
                'geometry', byteGeometry.decode()
            )

            root = et.Element("VergaraSoft")
            root = self.config.getXMLConfig(root)
            tree = et.ElementTree(root)
            tree.write(xmlFile)

        else:

            if configFile.is_file():

                tree = et.ElementTree(file=xmlFile)
                root = tree.getroot()
                self.config.setXMLConfig(root)

            else:

                configFile.touch(exist_ok=True)

    def restoreConfig(self):
        """Restore configuration if any"""

        bLogging = self.config.get('logging')
        if bLogging:
            self.actEnableLogging.setChecked(bLogging)
            self.enableLogging(bLogging)

        strGeometry = self.config.get('geometry')

        if strGeometry is not None:
            # Test for value read if not continue
            byteGeometry = strGeometry.encode()

            self.restoreGeometry(QByteArray.fromBase64(byteGeometry))

        else:

            self.setGeometry(0, 0, 1280, 720)
            self._center()


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
    app = QApplication(sys.argv)
    win = MKVMultiplexApp()
    win.show()
    app.exec_()
    logging.info("App End.")


if __name__ == "__main__":
    sys.exit(mainApp())
