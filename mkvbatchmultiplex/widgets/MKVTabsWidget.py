#!/usr/bin/env python3
"""Tabs Widget"""

import logging

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

MUTEX = QMutex()
MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVTabsWidget(QWidget):
    """Main Widget"""

    def __init__(self, parent, tab1Widget, tab2Widget, tab3Widget, tab4Widget):
        super(MKVTabsWidget, self).__init__(parent)

        self._initControls()
        self._initLayout(tab1Widget, tab2Widget, tab3Widget, tab4Widget)

    def _initControls(self):
        """Controls for Widget"""

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

    def _initLayout(self, tab1Widget, tab2Widget, tab3Widget, tab4Widget):
        """Setup Widget Layout"""

        self.layout = QVBoxLayout()

        # Add tabs
        self.tabs.addTab(self.tab1, "Command(s)")
        self.tabs.addTab(self.tab2, "Job(s)")
        self.tabs.addTab(self.tab3, "Job Output")
        self.tabs.addTab(self.tab4, "Job Error(s)")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(tab1Widget)
        self.tab1.setLayout(self.tab1.layout)

        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addWidget(tab2Widget)
        self.tab2.setLayout(self.tab2.layout)

        # Create third tab
        self.tab3.layout = QVBoxLayout(self)
        self.tab3.layout.addWidget(tab3Widget)
        self.tab3.setLayout(self.tab3.layout)

        # Create fourth tab
        self.tab4.layout = QVBoxLayout(self)
        self.tab4.layout.addWidget(tab4Widget)
        self.tab4.setLayout(self.tab4.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
