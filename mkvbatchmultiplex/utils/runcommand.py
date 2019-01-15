"""
RunCommand

Run a command in a subprocess and capture any output

if processLine function is provided it will be called
with every line read

if regexsearch regular expresion is provided the first
match will be set on regexmatch property
"""


import re
import shlex
import subprocess


class RunCommand:
    """
    Run system command in subprocess
    and save generated output

    :param command: command to execute
    :type command: str
    :param processLine: function called with every line read
    :type processLine: func
    :param regexsearch: regular expresion to search for match
    :type regexsearch: str
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

        except FileNotFoundError as e:
            self._error = e

        return rc
