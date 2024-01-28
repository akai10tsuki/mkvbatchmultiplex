#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
POC for CRC code to add it to name of file
"""

import re

from enum import Enum
from pathlib import Path, PurePath
from winreg import ConnectRegistry, HKEY_CURRENT_USER, QueryValueEx, OpenKey

from natsort import natsorted, ns

from PySide6.QtCore import Qt

from vsutillib.pyside6 import qtRunFunctionInThread, QRunInThread
from vsutillib.process import ThreadWorker, isThreadRunning
from vsutillib.files import crc32
from vsutillib.misc import isSystemInDarkMode

def mainCheck():

    numUnchecked = CheckState(1)

    b = (numUnchecked.value == Qt.CheckState.Unchecked.value)

    print(f"numUnchecked {numUnchecked} enum {Qt.CheckState.Unchecked} equal? {b}")

class CheckState(Enum):

    Unchecked = 0
    PartiallyChecked = 1
    Checked = 2

# from winreg import HKEY_CURRENT_USER as hkey, QueryValueEx as getSubkeyValue, OpenKey as getKey
def main():

    print(f"Windows is in DarkMode?={isSystemInDarkMode()}")

def mainEscape():
    """main"""

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    white = "\x1b[37;1m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    reWords = re.compile(r"^(.*?) (.*?) (.*?) ")

    d = Path(r"tests/NewFiles/MKVBatchMultiplex.log")

    if d.is_file():
        print("IS ALIVE!")

        with d.open(mode='r', encoding="UTF-8") as f:
            while line := f.readline():
                lineString = line.strip()
                reWords.match(lineString)
                #print(lineString)
                if matchWord := reWords.match(lineString):
                    level = matchWord[3]
                    if (level == "DEBUG"):
                        color = green
                    elif (level == "INFO"):
                        color = white
                    elif (level == "WARNING"):
                        color = yellow
                    elif (level == "ERROR"):
                        color = red
                    elif (level == "CRITICAL"):
                        color == bold_red
                    else:
                        color == reset
                    print(f"{color}{lineString}{reset}")
                else:
                    print("FUCK")

        # NOTSET = 0 = WHITE
        # DEBUG = 10 = GREEN
        # INFO = 20 = WHITE
        # WARNING = 30 = YELLOW
        # ERROR = 40 = RED
        # CRITICAL = 50 = PINK
    else:
        print("Whats going on.")

    #with open(filename) as file:
    #while line := file.readline():
    #    print(line.rstrip())


if __name__ == "__main__":
    main()