"""Utility functions"""


import platform
import re
import shlex
import subprocess
import sys


class RunCommand:
    """
    Run system command in subprocess
    and save generated output

    :param command: command to execute
    :type command: str
    :param processLine: function called with every line read
    :type processLine: func
    """

    def __init__(self, command, processLine=None, regexsearch=None):

        self._output = []
        self._command = command
        self._error = ""
        self._process = processLine
        self._regexmatch = None
        self._regEx = None
        if regexsearch is not None:
            self._regEx = re.compile(regexsearch)

    def __bool__(self):
        if self._command:
            return True
        return False

    def _reset(self, command=None):

        self._output = []
        self._error = ""
        if command is not None:
            self._command = command

    def run(self):
        """method to call to execute command"""
        self._reset()

        self._getCommandOutput()

        if self._output:
            return True

        return False

    @property
    def command(self):
        """command to execute"""
        return self._command

    @command.setter
    def command(self, value):
        self._reset(value)

    @property
    def error(self):
        """error if command can not be executed"""
        return self._error

    @property
    def output(self):
        """captured output"""
        return self._output

    @property
    def parsedcommand(self):
        """
        command parsed by shlex
        can be used for debugging
        """
        return shlex.split(self._command)

    @property
    def regexmatch(self):
        """results of regular expresion search"""
        return self._regexmatch

    def _regexMatch(self, line):

        m = None

        if self._regEx:
            m = self._regEx.search(line)

        if m is not None:
            if self._regexmatch is None:
                self._regexmatch = m.group(1)

    def _getCommandOutput(self):
        """Execute command in a subprocess"""

        rc = 10000
        cmd = shlex.split(self._command)

        try:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True,
                                  stderr=subprocess.PIPE) as p:

                for line in p.stdout:
                    self._output.append(line)
                    self._regexMatch(line)
                    if self._process is not None:
                        self._process(line)

                if p.returncode:
                    rc = p.returncode
                    print("return code {}".format(rc))

        except FileNotFoundError as e:
            self._error = e


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
