#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import os
import pathlib
import platform
import sys
import shlex

from pathlib import Path, PurePath

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QGridLayout,
    QWidget,
)

import vsutillib.mkv as mkv


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

        mkvmergeex = mkv.getMKVMerge()

        currentOS = platform.system()

        mkvmerge = shlex.quote(str(mkvmergeex))

        print(type(mkvmergeex).__name__)
        print(mkvmerge)

        if currentOS == "Windows":
            l = "--ui-language en"
        else:
            l = "--ui-language en_US"

        rootdir = pathlib.Path(__file__).parent.resolve()

        p = os.path.dirname(os.path.realpath(__file__))
        p = os.path.realpath(p)
        d = p + "/NewFiles"
        s = p + "/MediaFiles"
        e = os.path.isdir(d)
        if not e:
            os.mkdir(str(d))

        print(f"rootdir {rootdir}\nd       {p}\n")

        self.cmd0 = (
            mkvmerge
            + r" "
            + l
            + r" --output '"
            + d
            + r"/Show Title - S01E01.mkv' --language 0:und --track-name 0:x264 "
            + r"--language 1:jpn "
            + r"'(' '"
            + s
            + r"/avi/Show Title - S01E01.avi' ')' --language 0:eng '(' '"
            + s
            + r"/Subs/ass/ENG/Show Title - S01E01.ENG.ass' ')' --track-order 0:0,0:1,1:0"
        )

        # self.cmd1 = mkvmerge + r" " + l + r" --output '" + d + \
        #        r"/Show Title - S01E02.mkv' --language 0:und --language 1:spa " + \
        #        r"--default-track 1:yes " + \
        #        r"'(' '" + s + r"/mkv-nosubs/Show Title ' S01E02.mkv' ')' " + \
        #        r"--language 0:eng --default-track 0:yes " + \
        #        r"'(' '" + s + r"/Subs/ass/ENG/Show Title - S01E02.ENG.ass' ')'" + \
        #        r" --track-order 0:0,0:1,1:0"

        self.cmd1 = (
            mkvmerge
            + r" "
            + l
            + r" --output '"
            + d
            + r"/Show Title ' S01E02.mkv' --language 0:und "
            + r"--track-name '0:Video Name Test 02' --default-track 0:yes "
            + r"--display-dimensions 0:640x360 --language 1:ja "
            + r"--track-name '1:Original Audio' --default-track 1:yes "
            + r"'(' '"
            + s
            + r"/test/mkv/Show Title ' S01E02.mkv' ')' "
            + r"--language 0:en "
            + r"'(' '"
            + s
            + r"/test/mka/ENG/Show Title - S01E02.en.mka' ')' "
            + r"--language 0:en "
            + r"'(' '"
            + s
            + r"/test/subs/ENG/Show Title - S01E01.ENG.ass' ')' "
            + r"--attachment-name Font01.otf "
            + r"--attachment-mime-type application/vnd.ms-opentype "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font01.otf' "
            + r"--attachment-name Font02.otf "
            + r"--attachment-mime-type application/vnd.ms-opentype "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font02.otf' "
            + r"--attachment-name Font03.ttf "
            + r"--attachment-mime-type application/x-truetype-font "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font03.ttf' "
            + r"--attachment-name Font04.ttf "
            + r"--attachment-mime-type application/x-truetype-font "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font04.ttf' "
            + r"--title 'Show Title Number 2' "
            + r"--chapter-language und "
            + r"--chapters '"
            + s
            + r"/test/chapters/Show Title - S01E01 - Chapters.xml' "
            + r"--track-order 0:0,0:1,1:0,2:0"
        )

#            + r"/test/subs/ENG/Show Title - S01E01.ENG.ass' ')' "

        self.cmd2 = (
            mkvmerge
            + r" "
            + l
            + r" --output '"
            + d
            + r"/Show Title ' S01E02.mkv' --language 0:und "
            + r"--track-name '0:Video Name Test 02' --default-track 0:yes "
            + r"--display-dimensions 0:640x360 --language 1:ja --default-track 1:yes "
            + r"'(' '"
            + s
            + r"/test/mkv/Show Title ' S01E02.mkv' ')' "
            + r"--language 0:en --track-name '0:English Track' "
            + r"'(' '"
            + s
            + r"/test/mka/ENG/Show Title - S01E01.en.mka' ')' "
            + r"--language 0:en --track-name 0:English "
            + r"'(' '"
            + s
            + r"/test/subs/ENG/Show Title - S01E01.ENG.ass' ')' "
            + r"--no-audio --no-video --sub-charset 2:UTF-8 --language 2:es "
            + r"--track-name 2:Español --default-track 2:yes "
            + r"'(' '"
            + s
            + r"/test/subs/SPA/Show Title - S01E01.mkv' ')' "
            + r"--language 0:it --track-name 0:Italiano "
            + r"'(' '"
            + s
            + r"/test/subs/ITA/Show Title - S01E01.ITA.ass' ')' "
            + r"--attachment-name Font01.otf "
            + r"--attachment-mime-type application/vnd.ms-opentype "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font01.otf' "
            + r"--attachment-name Font02.otf "
            + r"--attachment-mime-type application/vnd.ms-opentype "
            + r"--attach-file '"
            + s
            + r"/test/Attachments/Font02.otf' "
            + r"--title 'Show Title Number 2' --chapter-language und "
            + r"--chapters '"
            + s
            + r"/test/chapters/Show Title - S01E01 - Chapters.xml' "
            + r"--track-order 0:0,0:1,1:0,2:0,3:0,4:2"
        )

        self.cmd3 = (
            mkvmerge
            + r" "
            + l
            + r" --output '"
            + d
            + r"/video'\''S01E05.mkv' --language 0:und --language 1:spa "
            + r"--default-track 1:yes '(' '"
            + s
            + r"/video'\''S01E05.avi' ')' --language 0:eng --default-track 0:yes '(' '"
            + s
            + r"/Subs/Video'\''S01E05.ass' ')' --track-order 0:0,0:1,1:0"
        )

        self.cmd4 = (
            mkvmerge
            + r" "
            + l
            + r" --output "
            + d
            + r"/video-S01E01.mkv --language 0:und --language 1:spa "
            + r"--default-track 1:yes '(' "
            + s
            + r"/video-S01E01.avi ')' --language 0:eng --default-track 0:yes '(' "
            + s
            + r"/Subs/Video-S01E01.ass ')' --track-order 0:0,0:1,1:0"
        )

        self.textWindow = QTextEdit()
        self.pushButton0 = QPushButton(" Command 0 ")
        self.pushButton0.resize(self.pushButton0.sizeHint())
        self.pushButton0.clicked.connect(  # pylint: disable=E1101
            lambda: self.pasteClipboard(0)
        )
        self.pushButton1 = QPushButton(" Command 1 ")
        self.pushButton1.resize(self.pushButton1.sizeHint())
        self.pushButton1.clicked.connect(  # pylint: disable=E1101
            lambda: self.pasteClipboard(1)
        )
        self.pushButton2 = QPushButton(" Command 2 ")
        self.pushButton2.resize(self.pushButton2.sizeHint())
        self.pushButton2.clicked.connect(   # pylint: disable=E1101
           lambda: self.pasteClipboard(2)
        )
        # self.pushButton3 = QPushButton(" Command 3 ")
        # self.pushButton3.resize(self.pushButton2.sizeHint())
        # self.pushButton3.clicked.connect(   # pylint: disable=E1101
        #    lambda: self.pasteClipboard(3)
        # )
        # self.pushButton4 = QPushButton(" Command 4 ")
        # self.pushButton4.resize(self.pushButton2.sizeHint())
        # self.pushButton4.clicked.connect(   # pylint: disable=E1101
        #    lambda: self.pasteClipboard(4)
        # )
        self.pushButtonExit = QPushButton(" Exit ")
        self.pushButtonExit.resize(self.pushButtonExit.sizeHint())
        self.pushButtonExit.clicked.connect(self.exitApp)  # pylint: disable=E1101

        self.textWindow.setText(self.cmd0)

        widget = QWidget()
        layout = QGridLayout(widget)
        layout.addWidget(self.textWindow, 0, 0, 7, 60)
        layout.addWidget(self.pushButton0, 7, 0)
        layout.addWidget(self.pushButton1, 7, 1)
        layout.addWidget(self.pushButton2, 7, 2)
        # layout.addWidget(self.pushButton3, 7, 3)
        # layout.addWidget(self.pushButton4, 7, 4)
        layout.addWidget(self.pushButtonExit, 7, 5)

        self.setCentralWidget(widget)

    def exitApp(self):
        """Exit"""

        self.close()

    def pasteClipboard(self, index):
        """Paste clipboard to command QLineEdit"""

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
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
