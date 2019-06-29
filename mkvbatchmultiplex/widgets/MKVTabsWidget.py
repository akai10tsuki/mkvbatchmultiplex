"""
Tabs Widget

Central widget holds:

    - Command widget
    - Jobs table widget
    - Jobs output
    - Jobs errors

"""
# MTW0001

import logging

from PySide2.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVTabsWidget(QWidget):
    """Main Widget"""

    log = False

    def __init__(self, parent, tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget):
        super(MKVTabsWidget, self).__init__(parent)

        self.parent = parent
        self._initControls()
        self._initLayout(tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget)


    def _initControls(self):
        """Controls for Widget"""

        # Initialize tab screen
        self.tabs = QTabWidget(self)

    def _initLayout(self, tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget):
        """Setup Widget Layout"""

        self.layout = QHBoxLayout()

        # Add tabs
        self.tabs.addTab(tab1Widget, "Command(s)")
        self.tabs.addTab(tab2Widget, "Job(s)")
        self.tabs.addTab(tab3Widget, "Job(s) Output")
        self.tabs.addTab(tab4Widget, "Job(s) Error(s)")
        self.tabs.addTab(tab5Widget, "Rename Files")

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
