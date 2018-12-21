
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate command line for testing
run this script and it will paste to the clipboard a command for testing
"""

import os
import sys

from PyQt5.QtWidgets import QApplication


def main():
    """main"""

    p = os.path.dirname(os.path.realpath(__file__))

    p = os.path.realpath(p)

    # pylint: disable=C0301
    cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output '" + p + \
            r"/NewFiles/video - S01E01.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' '" + p + \
            r"/VideoFiles/video - S01E01.avi' ')' --language 0:eng --default-track 0:yes '(' '" + p + \
            r"/VideoFiles/Video - S01E01.ass' ')' --track-order 0:0,0:1,1:0"

    app = QApplication(sys.argv)
    QApplication.clipboard().clear()
    QApplication.clipboard().setText(cmd)

    sys.exit()

if __name__ == "__main__":
    main()
