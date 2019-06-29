"""
Job info widget

format is Jobs: {:3d} Current Job: {:3d} File: {:3d} of {:3d} Errors: {:3d}

Jobs: total jobs
jobID: current running job
file: file number been work on current job
totalFiles: total files on current job
errors: total errors on current job
align:
    Qt.Horizontal - Horizontal layout the default
    Qt.Vertical - Vertical layout
"""


import random


from PySide2.QtWidgets import QWidget, QLabel
from PySide2.QtCore import Slot


class FormatLabel(QLabel):
    """
    Dual QProgressBar for unit and total progress

    param align - Set alignment Qt.Horizontal or Qt.Vertical
    type align - Qt.AlignmentFlags
    """
    #QLabel(QWidget *parent = nullptr, Qt::WindowFlags f = ...)
    #QLabel(const QString &text, QWidget *parent = nullptr, Qt::WindowFlags f = ...)

    def __init__(self, *args, **kwargs):
        #super(JobStatusLabel, self).__init__(*args, **kwargs)

        template = kwargs.pop('template', None)
        initValues = kwargs.pop('init', None)

        if (args) or (template is not None):
            if initValues is None:
                raise KeyError("init= not specified")

            if args:
                if isinstance(args[0], str):
                    template = args[0]
                    args = args[1:]

        if initValues is None:
            initValues = []

        super().__init__(*args, **kwargs)

        if template is None:
            self._template = \
                "Job(s): {0:3d} Running: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}"
            initValues = [0, 0, 0, 0, 0]
        else:
            self._template = template

        self._values = initValues
        self._refresh()

    def __getitem__(self, index):
        return self._values[index]

    def __setitem__(self, index, value):
        self._values[index] = value
        self._refresh()

    def _refresh(self):

        strTmp = self._template
        strTmp = strTmp.format(*self._values)
        super().setText(strTmp)

    @Slot(list)
    def setValues(self, args):
        """
        Set Values

        :param args: set values
        :type args: list
        """

        self._values = list(args)
        self._refresh()

    @Slot(int, object)
    def setValue(self, index, value):
        """
        Set value index based

        :param index: index position
        :type index: int
        :param value: value to set
        :type value: object
        """

        self._values[index] = value
        self._refresh()

    @property
    def values(self):
        """return current positional values"""

        return self._values

    def valuesConnect(self, signal):
        """make connection to setValues Slot"""

        signal.connect(self.setValues)

    def valueConnect(self, signal):
        """make connection to setValues Slot"""

        signal.connect(self.setValue)

if __name__ == '__main__':

    import sys
    from PySide2.QtWidgets import QApplication, QGridLayout, QMainWindow, QPushButton

    class MainWindow(QMainWindow):
        """Test the progress bars"""

        def __init__(self, *args, **kwargs):
            super(MainWindow, self).__init__(*args, **kwargs)

            l = QGridLayout()

            self.jobInfo = FormatLabel()
            self.formatLabel = FormatLabel("Random 1 = {0:>3d} -- Random 2 = {0:3d}", init=[0, 0])

            b = QPushButton("Test 1")
            b.pressed.connect(self.test)
            b1 = QPushButton("Test 2")
            b1.pressed.connect(self.test1)
            l.addWidget(self.jobInfo, 0, 0)
            l.addWidget(self.formatLabel, 1, 0)
            l.addWidget(b, 4, 0)
            l.addWidget(b1, 5, 0)

            w = QWidget()
            w.setLayout(l)

            self.setCentralWidget(w)

            self.show()

        def test(self):
            """Test"""

            r = random.randint

            self.jobInfo.setValues(
                (r(1, 1001),
                 r(1, 1001),
                 r(1, 1001),
                 r(1, 1001),
                 r(1, 1001))
            )

        def test1(self):
            """Test FormatLabel"""
            r = random.randint

            self.formatLabel[0] = r(1, 1001)
            self.formatLabel[1] = r(1, 1001)

    # pylint: disable=C0103
    # variables use to construct application not constants
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())
