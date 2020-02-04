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

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QTabWidget

from ..utils import Text

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class TabsWidget(QTabWidget):
    """Main Widget"""

    # Class logging state
    __log = False

    setCurrentIndexSignal = Signal(int)
    setCurrentWidgetSignal = Signal(object)

    def __init__(
        self, parent, tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget
    ):
        super(TabsWidget, self).__init__()

        self.parent = parent

        self.__log = False

        self._initUI(tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget)
        self.setCurrentIndexSignal.connect(super().setCurrentIndex)
        self.setCurrentWidgetSignal.connect(super().setCurrentWidget)

    def _initUI(self, tab1Widget, tab2Widget, tab3Widget, tab4Widget, tab5Widget):
        """Setup Widget Layout"""

        self.addTab(tab1Widget, 'Command(s)')
        self.addTab(tab2Widget, 'Job(s)')
        self.addTab(tab3Widget, 'Job(s) Output')
        self.addTab(tab4Widget, 'Job(s) Error(s)')
        self.addTab(tab5Widget, 'Rename Files')

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:
                returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return TabsWidget.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def setLanguage(self):
        """
        setLanguage set tabs labels according to locale
        """

        self.setTabText(0, _(Text.txt0132) + "(s)")
        self.setTabText(1, _(Text.txt0140) + "(s)")
        self.setTabText(2, _(Text.txt0141))
        self.setTabText(3, _(Text.txt0142))
        self.setTabText(4, _(Text.txt0143))
