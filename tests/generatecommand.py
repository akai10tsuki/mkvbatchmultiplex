
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QGridLayout, QWidget


class GenCommandApp(QMainWindow):
    """Generate command line"""

    def __init__(self, parent=None):
        super(GenCommandApp, self).__init__(parent)

        p = os.path.dirname(os.path.realpath(__file__))
        p = os.path.realpath(p)
        d = p + "/NewFiles"
        e = os.path.isdir(d)
        if not e:
            os.mkdir(str(d))

        # pylint: disable=C0301
        self.cmd0 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output '" + p + \
                r"/NewFiles/video - S01E01.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + p + \
                r"/VideoFiles/video - S01E01.avi' ')' --language 0:eng --default-track 0:yes '(' '" + p + \
                r"/VideoFiles/Video - S01E01.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output '" + p + \
                r"/NewFiles/video - S01E02.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + p + \
                r"/VideoFiles/video - S01E02.avi' ')' --language 0:eng --default-track 0:yes '(' '" + p + \
                r"/VideoFiles/Video - S01E02.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd2 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output '" + p + \
                r"/NewFiles/video - S01E03.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + p + \
                r"/VideoFiles/video - S01E03.avi' ')' --language 0:eng --default-track 0:yes '(' '" + p + \
                r"/VideoFiles/Video - S01E03.ass' ')' --track-order 0:0,0:1,1:0"

        self.textWindow = QTextEdit()
        self.pushButton0 = QPushButton(" Command 0 ")
        self.pushButton0.resize(self.pushButton0.sizeHint())
        self.pushButton0.clicked.connect(
            lambda: self.pasteClipboard(0)
        )
        self.pushButton1 = QPushButton(" Command 1 ")
        self.pushButton1.resize(self.pushButton1.sizeHint())
        self.pushButton1.clicked.connect(
            lambda: self.pasteClipboard(1)
        )
        self.pushButton2 = QPushButton(" Command 2 ")
        self.pushButton2.resize(self.pushButton2.sizeHint())
        self.pushButton2.clicked.connect(
            lambda: self.pasteClipboard(2)
        )
        self.pushButtonExit = QPushButton(" Exit ")
        self.pushButtonExit.resize(self.pushButtonExit.sizeHint())
        self.pushButtonExit.clicked.connect(
            self.exitApp
        )

        self.textWindow.setText(self.cmd0)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.addWidget(self.textWindow, 0, 0, 7, 60)
        layout.addWidget(self.pushButton0, 7, 0)
        layout.addWidget(self.pushButton1, 7, 1)
        layout.addWidget(self.pushButton2, 7, 2)
        layout.addWidget(self.pushButtonExit, 7, 3)

        self.setCentralWidget(widget)

    def exitApp(self):
        """Exit"""

        self.close()

    def pasteClipboard(self, index):
        """Paste clipboard to command QLineEdit"""

        print(index)
        cmd = self.cmd0
        if index == 1:
            cmd = self.cmd1
            print("change 1")
        elif index == 2:
            cmd = self.cmd2
            print("change 2")

        QApplication.clipboard().clear()
        QApplication.clipboard().setText(cmd)
        self.textWindow.clear()
        self.textWindow.setText(cmd)


def main():
    """main"""

    app = QApplication(sys.argv)
    win = GenCommandApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
