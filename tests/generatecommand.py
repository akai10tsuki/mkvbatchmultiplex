
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import glob
import os
import platform
import sys

from pathlib import Path, PurePath

from PySide2.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QGridLayout, QWidget

def findFile(element, dirPath=None):

    if dirPath is None:
        dirPath = os.getenv('PATH')

    dirs = dirPath.split(os.pathsep)

    for dirname in dirs:
        candidate = Path(PurePath(dirname).joinpath(element))
        if candidate.is_file():
            return candidate

    return None

def getMKVMerge():

    # /Applications/MKVToolNix-29.0.0.app/Contents/MacOS/mkvmerge
    currentOS = platform.system()

    if currentOS == "Darwin":
        lstTest = glob.glob("/Applications/MKVToolNix*")
        if lstTest:
            f = lstTest[0] + "/Contents/MacOS/mkvmerge"
            mkvmerge = Path(f)
            if mkvmerge.is_file():
                return mkvmerge

    elif currentOS == "Windows":
        #ProgramFiles=C:\Program Files
        #ProgramFiles(x86)=C:\Program Files (x86)

        defPrograms64 = os.environ.get('ProgramFiles')
        defPrograms32 = os.environ.get('ProgramFiles(x86)')

        dirs = []
        if defPrograms64 is not None:
            dirs.append(defPrograms64)

        if defPrograms32 is not None:
            dirs.append(defPrograms32)

        # search 64 bits
        for d in dirs:
            search = sorted(Path(d).rglob("mkvmerge.exe"))
            if search:
                mkvmerge = Path(search[0])
                if mkvmerge.is_file():
                    return mkvmerge

    elif currentOS == "Linux":

        search = findFile("mkvmerge")

        if search is not None:
            mkvmerge = Path(search)
            if mkvmerge.is_file():
                return mkvmerge

    return None

def checkForQuote(file):

    f = str(file)

    if f.find(" ") >= 0:
        return "'" + f + "'"

    return f


class GenCommandApp(QMainWindow):
    """Generate command line"""

    def __init__(self, parent=None):
        super(GenCommandApp, self).__init__(parent)

        mkvmergeex = getMKVMerge()

        if mkvmergeex:
            mkvmerge = checkForQuote(mkvmergeex)

        p = os.path.dirname(os.path.realpath(__file__))
        p = os.path.realpath(p)
        d = p + "/NewFiles"
        s = p + "/VideoFiles"
        e = os.path.isdir(d)
        if not e:
            os.mkdir(str(d))

        # pylint
        self.cmd0 = mkvmerge + r" --ui-language en --output '" + d + \
                r"/video - S01E01.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + s + \
                r"/video - S01E01.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video - S01E01.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd1 = mkvmerge + r" --ui-language en --output '" + d + \
                r"/video - S01E02.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + s + \
                r"/video - S01E02.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video - S01E02.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd2 = mkvmerge + r" --ui-language en --output '" + d + \
                r"/video - S01E03.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + s + \
                r"/video - S01E03.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video - S01E03.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd3 = mkvmerge + r" --ui-language en --output " + d + \
                r"/video-S01E01.mkv --language 0:und --language 1:spa --default-track 1:yes '(' " + s + \
                r"/video-S01E01.avi ')' --language 0:eng --default-track 0:yes '(' " + s + \
                r"/Video-S01E01.ass ')' --track-order 0:0,0:1,1:0"


        self.textWindow = QTextEdit()
        self.pushButton0 = QPushButton(" Command 0 ")
        self.pushButton0.resize(self.pushButton0.sizeHint())
        self.pushButton0.clicked.connect(
            lambda: self.pasteClipboard(0)
        )
        self.pushButton0.clicked.
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
