#!/usr/bin/env python3

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

class JobStatusLabel(QLabel):
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
            print("First Arg = {}", args[0])
            print("Args = {}".format(args))
            if initValues is None:
                raise KeyError("init= not specified")

        super().__init__(*args, **kwargs)

        if template is None:
            self._template = \
                "Jobs: {0:3d} Current Job: {1:3d} File: {2:3d} of {3:3d} Errors: {4:3d}"
        else:
            self._template = template

        self._intHelper()

    def _intHelper(self):

        strTmp = self._template
        newText = strTmp.format(0, 0, 0, 0, 0)
        print("New {}", newText)

        self.setText(newText)

    def setText(self, arg):

        print(arg, type(arg))

        super().setText(arg)

    @Slot(dict)
    def setValues(self, *arg):
        """
        Set Values

        : param align: Set alignment Qt.Horizontal or Qt.Vertical
        : type align: Qt.AlignmentFlags
        """
        strTmp = self._template
        strTmp = strTmp.format(*arg)
        self.setText(strTmp)

if __name__ == '__main__':

    import sys
    from PySide2.QtWidgets import QApplication, QGridLayout, QMainWindow, QPushButton

    class MainWindow(QMainWindow):
        """Test the progress bars"""

        def __init__(self, *args, **kwargs):
            super(MainWindow, self).__init__(*args, **kwargs)

            l = QGridLayout()

            self.jobInfo = JobStatusLabel("Argument {}")

            b = QPushButton("Test")
            b.pressed.connect(self.test)
            l.addWidget(self.jobInfo, 0, 0)
            l.addWidget(b, 1, 0)

            w = QWidget()
            w.setLayout(l)

            self.setCentralWidget(w)

            self.show()

        def test(self):
            """Test"""

            r = random.randint

            self.jobInfo.setValues(
                r(1, 1001),
                r(1, 1001),
                r(1, 1001),
                r(1, 1001),
                r(1, 1001)
            )

    # pylint: disable=C0103
    # variables use to construct application not constants
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())
