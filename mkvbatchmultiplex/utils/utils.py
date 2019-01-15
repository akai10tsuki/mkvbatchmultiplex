"""Utility functions"""


import platform
import shlex
import subprocess
import sys

from .runcommand import RunCommand

def getCommandOutput(command, lstOutput):
    """Execute command in a subprocess thread"""

    rc = 10000
    cmd = shlex.split(command)

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True,
                          stderr=subprocess.PIPE) as p:

        for line in p.stdout:

            lstOutput.append(line)
            rcResult = p.poll()
            if rcResult is not None:
                rc = rcResult

    return rc

def isMacDarkMode():
    """Test for macOS Dark Mode"""

    if platform.system() == "Darwin":
        cmd = RunCommand("defaults read -g AppleInterfaceStyle")

        if getattr(sys, 'frozen', False):
            return False

        if cmd.run():
            for e in cmd.output:
                if e.find("Dark") >= 0:
                    return True

    return False
