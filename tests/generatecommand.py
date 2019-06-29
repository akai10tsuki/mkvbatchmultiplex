
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import os
import platform
import sys
import shlex

from pathlib import Path, PurePath


from PySide2.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QGridLayout, QWidget
)


import vsutillib as utils



#def findFile(element, dirPath=None):
#    """find file in the path"""

#    if dirPath is None:
#        dirPath = os.getenv('PATH')

#    dirs = dirPath.split(os.pathsep)

#    for dirname in dirs:
#        candidate = Path(PurePath(dirname).joinpath(element))
#        if candidate.is_file():
#            return candidate

#    return None


#def getMKVMerge():
#    """Looks for mkvmerge executable in the system"""

    # /Applications/MKVToolNix-29.0.0.app/Contents/MacOS/mkvmerge
#    currentOS = platform.system()

#    if currentOS == "Darwin":
#        lstTest = glob.glob("/Applications/MKVToolNix*")
#        if lstTest:
#            f = lstTest[0] + "/Contents/MacOS/mkvmerge"
#            mkvmerge = Path(f)
#            if mkvmerge.is_file():
#                return mkvmerge

#    elif currentOS == "Windows":
        #ProgramFiles=C:\Program Files
        #ProgramFiles(x86)=C:\Program Files (x86)

#        defPrograms64 = os.environ.get('ProgramFiles')
#        defPrograms32 = os.environ.get('ProgramFiles(x86)')

#        dirs = []
#        if defPrograms64 is not None:
#            dirs.append(defPrograms64)

#        if defPrograms32 is not None:
#            dirs.append(defPrograms32)

        # search 64 bits
#        for d in dirs:
#            search = sorted(Path(d).rglob("mkvmerge.exe"))
#            if search:
#                mkvmerge = Path(search[0])
#                if mkvmerge.is_file():
#                    return mkvmerge

#    elif currentOS == "Linux":

#        search = findFile("mkvmerge")

#        if search is not None:
#            mkvmerge = Path(search)
#            if mkvmerge.is_file():
#                return mkvmerge

#    return None


def checkForQuote(file):
    """add quotes if find spaces in file name"""

    f = str(file)

    if f.find(" ") >= 0:
        return "'" + f + "'"

    return f


class GenCommandApp(QMainWindow):
    """Generate command line"""

    def __init__(self, parent=None):
        super(GenCommandApp, self).__init__(parent)

        mkvmergeex = utils.mkv.getMKVMerge()

        currentOS = platform.system()

        mkvmerge = shlex.quote(str(mkvmergeex))

        print(type(mkvmergeex).__name__)
        print(mkvmerge)

        if currentOS == "Windows":
            l = "--ui-language en"
        else:
            l = "--ui-language en_US"


        p = os.path.dirname(os.path.realpath(__file__))
        p = os.path.realpath(p)
        d = p + "/NewFiles"
        s = p + "/VideoFiles"
        e = os.path.isdir(d)
        if not e:
            os.mkdir(str(d))

        self.cmd0 = mkvmerge + r" " + l + " --output '" + d + \
                r"/video-S01E01.mkv' --language 0:und --language 1:spa " + \
                r"--default-track 1:yes '(' '" + s + \
                r"/video-S01E01.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video-S01E01.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd1 = mkvmerge + r" " + l + " --output '" + d + \
                r"/video - S01E02.mkv' --language 0:und --language 1:spa " + \
                r"--default-track 1:yes '(' '" + s + \
                r"/video - S01E02.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video - S01E02.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd2 = mkvmerge + r" " + l + " --output '" + d + \
                r"/video - S01E03.mkv' --language 0:und --language 1:spa " + \
                r"--default-track 1:yes '(' '" + s + \
                r"/video - S01E03.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video - S01E03.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd3 = mkvmerge + r" " + l + " --output '" + d + \
                r"/video'\''S01E05.mkv' --language 0:und --language 1:spa " + \
                r"--default-track 1:yes '(' '" + s + \
                r"/video'\''S01E05.avi' ')' --language 0:eng --default-track 0:yes '(' '" + s + \
                r"/Video'\''S01E05.ass' ')' --track-order 0:0,0:1,1:0"

        self.cmd4 = mkvmerge + r" " + l + " --output " + d + \
                r"/video-S01E01.mkv --language 0:und --language 1:spa " + \
                r"--default-track 1:yes '(' " + s + \
                r"/video-S01E01.avi ')' --language 0:eng --default-track 0:yes '(' " + s + \
                r"/Video-S01E01.ass ')' --track-order 0:0,0:1,1:0"


        self.textWindow = QTextEdit()
        self.pushButton0 = QPushButton(" Command 0 ")
        self.pushButton0.resize(self.pushButton0.sizeHint())
        self.pushButton0.clicked.connect(   # pylint: disable=E1101
            lambda: self.pasteClipboard(0)
        )
        self.pushButton1 = QPushButton(" Command 1 ")
        self.pushButton1.resize(self.pushButton1.sizeHint())
        self.pushButton1.clicked.connect(   # pylint: disable=E1101
            lambda: self.pasteClipboard(1)
        )
        self.pushButton2 = QPushButton(" Command 2 ")
        self.pushButton2.resize(self.pushButton2.sizeHint())
        self.pushButton2.clicked.connect(   # pylint: disable=E1101
            lambda: self.pasteClipboard(2)
        )
        self.pushButton3 = QPushButton(" Command 3 ")
        self.pushButton3.resize(self.pushButton2.sizeHint())
        self.pushButton3.clicked.connect(   # pylint: disable=E1101
            lambda: self.pasteClipboard(3)
        )
        self.pushButton4 = QPushButton(" Command 4 ")
        self.pushButton4.resize(self.pushButton2.sizeHint())
        self.pushButton4.clicked.connect(   # pylint: disable=E1101
            lambda: self.pasteClipboard(4)
        )
        self.pushButtonExit = QPushButton(" Exit ")
        self.pushButtonExit.resize(self.pushButtonExit.sizeHint())
        self.pushButtonExit.clicked.connect(    # pylint: disable=E1101
            self.exitApp
        )

        self.textWindow.setText(self.cmd0)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.addWidget(self.textWindow, 0, 0, 7, 60)
        layout.addWidget(self.pushButton0, 7, 0)
        layout.addWidget(self.pushButton1, 7, 1)
        layout.addWidget(self.pushButton2, 7, 2)
        layout.addWidget(self.pushButton3, 7, 3)
        layout.addWidget(self.pushButton4, 7, 4)
        layout.addWidget(self.pushButtonExit, 7, 5)

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
        elif index == 2:
            cmd = self.cmd2
        elif index == 3:
            cmd = self.cmd3
        elif index == 4:
            cmd = self.cmd4

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
