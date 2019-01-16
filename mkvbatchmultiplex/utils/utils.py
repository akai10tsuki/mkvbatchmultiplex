"""Utility functions"""


import platform
import sys

from .runcommand import RunCommand


def isMacDarkMode():
    """Test for macOS Dark Mode"""

    if platform.system() == "Darwin":
        cmd = RunCommand("defaults read -g AppleInterfaceStyle")

        if getattr(sys, 'frozen', False):
            # running in pyinstaller bundle dark mode does not apply
            return False

        if cmd.run():
            for e in cmd.output:
                if e.find("Dark") >= 0:
                    return True

    return False
