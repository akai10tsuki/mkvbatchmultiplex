
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QTextEdit, QPushButton, QGridLayout, QWidget


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
        self.cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output '" + p + \
                r"/NewFiles/video - S01E01.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + p + \
                r"/VideoFiles/video - S01E01.avi' ')' --language 0:eng --default-track 0:yes '(' '" + p + \
                r"/VideoFiles/Video - S01E01.ass' ')' --track-order 0:0,0:1,1:0"

        self.textWindow = QTextEdit()
        self.pushButton = QPushButton(" Copy to Clipboard ")
        self.pushButton.resize(self.pushButton.sizeHint())
        self.pushButton.clicked.connect(
            self.pasteClipboard
        )

        self.textWindow.setText(self.cmd)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.addWidget(self.textWindow, 0, 0, 7, 60)
        layout.addWidget(self.pushButton, 7, 30)

        self.setCentralWidget(widget)

    def pasteClipboard(self):
        """Paste clipboard to command QLineEdit"""

        QApplication.clipboard().clear()
        QApplication.clipboard().setText(self.cmd)
        self.close()


def main():
    """main"""

    app = QApplication(sys.argv)
    win = GenCommandApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
