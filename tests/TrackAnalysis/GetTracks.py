"""
GetTracks Class: get tracks using mkvmerge --identify

Output widget form just to output text in color
"""
# GTK0001 Next log ID

import logging
import shlex

from pathlib import Path


from vsutillib.mkv import getMKVMerge
from vsutillib.process import RunCommand

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class GetTracks:
    """Output for running queue"""

    # logging state
    __log = False

    def __init__(self, fileName=None, log=None):

        self.__log = None
        self.log = log
        self.mkvmerge = None

        self._initVars()

        if mkvmerge := getMKVMerge():
            self.mkvmerge = mkvmerge
        else:
            self.__errorFound = True

        if fileName is not None:
            self.fileName = fileName

    def _initVars(self):
        self.__errorFound = False
        self.__fileName = None
        self.__output = None

    #
    # Logging setup
    #

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return GetTracks.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    @property
    def fileName(self):
        return self.__fileName

    @fileName.setter
    def fileName(self, value):
        if isinstance(value, Path):
            self.__fileName = value
        else:
            self.__fileName = Path(value)
        self.getTracks()

    @property
    def output(self):
        return self.__output

    def getTracks(self):

        if not self.__errorFound:
            runCommand = RunCommand(shlex.quote(str(self.mkvmerge)) + " --identify " + shlex.quote(str(self.__fileName)))

            if runCommand.run():
                self.__output = runCommand.output
            else:
                self.__output = None
