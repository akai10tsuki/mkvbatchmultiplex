#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This class is used to construct the list used to execute the MKVMerge
command line

strCommand = Command obtained from mkvtoolnix-gui with the modifications
    needed for Multiplexing a series in a directory

path for executable and target options are parsed from the command line

MC018
"""

import ast
import os
import re
import shlex
import logging

from pathlib import Path

import mkvbatchmultiplex.utils as utils

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class MKVCommand(object):
    """
    Class to work with mkvmerge command

    :param strCommand: command line as generated by mkvtoolnix-gui
    :type strCommand: str
    :param bRemoveTitle: remove title from command
    :type bRemoveTitle: bool
    """

    log = False

    def __init__(self, strCommand=None, bRemoveTitle=True):

        self._strShellcommand = ""
        self._oDestinationFile = None
        self._oBaseSourceFilesList = []
        self._lstCommandTemplate = []
        self._lstCommands = []
        self._bInconsistent = False
        self._strError = ""
        self._bRaiseError = False
        self._workFiles = WorkFiles()
        self._index = 0
        self._initHelper(strCommand, bRemoveTitle)

        if strCommand is not None:
            self._GenerateCommands()

    def _initHelper(self, strCommand, bRemoveTitle=True):

        if strCommand is None:

            self._reset()

        else:

            self._strShellcommand = strCommand
            self._bInconsistent = False
            self._strError = ""

            if MKVCommand.bLooksOk(strCommand):

                #Substitute file names for shlex help with apostrophe
                lstFileNames = []
                dictFileNames = {}
                dictFileTokens = {}
                lstParsed = []

                strCommand = _strStripEscapeChars(strCommand)

                _parseSourceFiles(strCommand, lstFileNames,
                                  dictFileNames, dictFileTokens, MKVCommand.log)

                if lstFileNames:

                    for strFile in lstFileNames:
                        strCommand = strCommand.replace(
                            strFile, dictFileTokens[strFile])

                    lstParsed = shlex.split(strCommand)

                    for t in enumerate(lstParsed):
                        if lstParsed[t[0]] in dictFileNames:
                            lstParsed[t[0]] = dictFileNames[t[1]]

                    self._oDestinationFile = MKVSourceFile(
                        lstParsed.index("--output") + 1,
                        lstParsed[lstParsed.index("--output") + 1]
                    )

                else:
                    self._bInconsistent = True
                    self._strError = "No output file found."

                # Windows present inconsistent use of
                # forward and backward slash fix for
                # windows
                #ft = Path(lstParsed[0])
                #lstParsed[0] = str(ft)

                if bRemoveTitle and lstParsed:
                    #Remove title if found since this is for batch processing
                    #the title will propagate to all the files maybe erroneously.
                    #This parameters are preserved from the source files.

                    while "--title" in lstParsed:

                        i = lstParsed.index("--title")
                        del lstParsed[i:i+2]

                # Get the index of files surrounded by parenthesis these
                # are source files there have to be at least one
                lstIndices = [i for i, x in enumerate(lstParsed) if x == "("]

                # Store source files in list
                j = 0
                for i in lstIndices:
                    self._oBaseSourceFilesList.append(
                        MKVSourceFile(i - (j * 2),
                                      lstParsed[i + 1])
                    )
                    j += 1

                # Remove parenthesis it does not work for the subprocess
                # execution
                lstParsed = [
                    i for i in lstParsed if (i != "(") and (i != ")")
                ]

                self._lstCommandTemplate.extend(lstParsed)

                self._lstCommandTemplate[self._oDestinationFile.index] = ""

                for objFile in self._oBaseSourceFilesList:

                    self._lstCommandTemplate[objFile.index] = ""

            else:

                self._bInconsistent = True
                self._strError = "Error parsing command line."

            if self._bInconsistent:
                self._lstCommandTemplate = []
                if MKVCommand.log:
                    MODULELOG.error("MC001: ".join(self._strError))

    def _reset(self):
        """Reset variable properties"""
        self._strShellcommand = ""
        self._oDestinationFile = None
        self._oBaseSourceFilesList = []
        self._lstCommandTemplate = []
        self._lstCommands = []
        self._bInconsistent = False
        self._bRaiseError = False
        self._strError = ""
        self._index = 0

    def __bool__(self):
        return not (self._bInconsistent or (self._strShellcommand == "") or self._bRaiseError)

    def __contains__(self, item):
        return item in self._lstCommands

    def __getitem__(self, index):
        return [self._lstCommands[index], self._workFiles.baseFiles,
                self._workFiles.sourceFiles[index]]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._lstCommands)

    def __next__(self):
        if self._index >= len(self._lstCommands):
            self._index = 0
            raise StopIteration
        else:
            self._index += 1
            return [self._lstCommands[self._index - 1], self._workFiles.baseFiles,
                    self._workFiles.sourceFiles[self._index - 1]]

    def _GenerateCommands(self):

        self._getFiles()

        if self._workFiles.sourceFiles:
            for lstFiles in self._workFiles.sourceFiles:
                lstProcessCommand = self._setFiles(lstFiles)
                # list assigns a copy of lstProcessCommand not the object
                self._lstCommands.append(lstProcessCommand)

    def _getFiles(self, log=False):
        """read source directories to get files"""

        self._workFiles.sourceFiles = []

        lstMKVFiles = []
        lstTypeTotal = []

        # Get files from any directory found in command
        # the number of files on each directory has to be equal
        # Filter by type in original source file

        if self._oBaseSourceFilesList:

            self._workFiles.baseFiles = [x.fullPathName for x in self._oBaseSourceFilesList]

            for objFile in self._oBaseSourceFilesList:
                lstMKVFiles.append(
                    utils.getFileList(
                        objFile.directory,
                        objFile.extension,
                        True
                    )
                )

            if self._bCheckLenOfLists(lstMKVFiles, lstTypeTotal):
                # Join all source files in a list of lists each element
                # have all source files in the order found
                # The names are not used to pair the order in the
                # directories is
                for i in range(len(lstMKVFiles[0])):
                    self._workFiles.sourceFiles.append([x[i] for x in lstMKVFiles])

            else:

                self._bRaiseError = True
                error = "UT002: List of files total don't match."
                self._strError = error + "\n\n"
                if log:
                    MODULELOG.error("UT003: List of files total don't match")
                for lstTmp in lstTypeTotal:
                    error = lstTmp[0] + " - " + lstTmp[1]
                    self._strError = self._strError + error + "\n"
                    if log:
                        MODULELOG.error("UT004: File(s): %s", error)

    def _bCheckLenOfLists(self, lstLists, lstTypeTotal):
        """list of source files has to be equal length"""

        intTmp = None
        bReturn = True

        for lstTmp in lstLists:

            if not lstTmp:
                bReturn = False
                lstTypeTotal.append(("Ops!!!", "File(s) not found."))
                break

            lstTypeTotal.append([str(len(lstTmp)), os.path.splitext(lstTmp[0])[1]])

            if not intTmp:
                #length of first list is base for comparison
                intTmp = len(lstTmp)
            else:
                if len(lstTmp) != intTmp:
                    #not equal fail test
                    if bReturn:
                        bReturn = False

        return bReturn

    def _setFiles(self, lstFiles, strPrefix="new-"):
        """
        Substitute file names on command template

        :param lstFiles: list of files in command line to process
        :type lstFiles: list
        :param strPrefix: prefix for output files
        :type strPrefix: str
        """

        lstProcessCommand = []

        if not self._bInconsistent:

            lstProcessCommand = [x for x in self._lstCommandTemplate]

            _, filename = os.path.split(lstFiles[0])

            strTmp = os.path.join(
                self._oDestinationFile.directory,
                os.path.splitext(filename)[0] +
                self._oDestinationFile.extension
            )

            # Check if destination file exist and add prefix if it does
            if os.path.isfile(strTmp):
                strSuffix = ""
                n = 1
                while True:
                    strDestinationFile = os.path.join(
                        self._oDestinationFile.directory,
                        strPrefix
                        + os.path.splitext(filename)[0]
                        + strSuffix
                        + self._oDestinationFile.extension
                    )

                    if os.path.isfile(strDestinationFile):
                        strSuffix = " (%d)" % n
                        n += 1
                    else:
                        break
            else:
                strDestinationFile = strTmp

            lstProcessCommand[self._oDestinationFile.index] = strDestinationFile

            for objFile, strFile in zip(self._oBaseSourceFilesList, lstFiles):
                lstProcessCommand[objFile.index] = strFile

        else:

            lstProcessCommand = []

        # return a copy of list not the object lstProcessCommand
        return [x for x in lstProcessCommand]

    @property
    def basefiles(self):
        """return base files list"""

        return self._workFiles.baseFiles

    @property
    def sourcefiles(self):
        """
        property to return the working source files
        """

        return self._workFiles.sourceFiles

    @property
    def command(self):
        """
        property command produced by mkvtoolnix-gui can be set
        """
        return self._strShellcommand

    @command.setter
    def command(self, value):
        """Update command through property"""
        if isinstance(value, str):
            self._reset()
            self._initHelper(value)
            self._GenerateCommands()

    @property
    def error(self):
        """return error description"""

        return self._strError

    @property
    def template(self):
        """
        constructed command template
        """

        return self._lstCommandTemplate

    @staticmethod
    def bLooksOkOld(strCmd, lstResults=None):
        """
        Sanity check on command any failure results in no action whatsoever
        and since the original are not modified the resulting command should be safe

        :param strCommand: command line as generated by mkvtoolnix-gui
        :type strCommand: str
        :param lstResults: list to put analysis messages
        :type lstResults: list
        :rtype: bool
        """

        if not strCmd:
            return False

        strCommand = _strStripEscapeChars(strCmd)  # Comvert line to bash style

        lstAnalysis = []

        #rg = r"^'(.*?)'\s.*?\-\-output.'(.*?)'\s.*?\s'\('\s'(.*?)'\s'\)'.*?\-\-track-order\s(.*)"  # pylint: disable=C0301
        rg = r"^'?(.*?)'\s.*?\-\-output.'(.*?)'\s.*?\s'\('\s'(.*?)'\s'\)'.*?\-\-track-order\s(.*)"  # pylint: disable=C0301
        regCommandEx = re.compile(rg)
        matchCommand = regCommandEx.match(strCommand)

        reExecutableEx = re.compile(r"^'(.*?)'")
        matchExecutable = reExecutableEx.match(strCommand)

        reOutputFileEx = re.compile(r".*?\-\-output.'(.*?)'")
        matchOutputFile = reOutputFileEx.match(strCommand)

        reSourcesEx = re.compile(r"'\('\s'(.*?)'\s'\)'")
        matchSources = reSourcesEx.finditer(strCommand)

        reAttachmentsEx = re.compile(r"\-\-attach-file.'(.*?)'")
        matchAttachments = reAttachmentsEx.finditer(strCommand)

        bOk = True
        trackOrder = None
        # To look Ok must match the 5 group in the command line that
        # are expected
        # 1: mkvmerge name with fullpath
        # 2: output file
        # 3: at list one source
        # 4: track order
        if matchCommand and (len(matchCommand.groups()) == 4):
            lstAnalysis.append("Command seems ok.")
            trackOrder = matchCommand.group(4)
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Command bad format.")
            bOk = False

        if trackOrder is not None:
            try:
                d = ast.literal_eval("{" + trackOrder + "}")
                trackTotal = MKVCommand.numberOfTracks(strCommand)

                s = trackOrder.split(',')
                if trackTotal == len(s):
                    for e in s:
                        if not e.find(':') > 0:
                            bOk = False
                else:
                    bOk = False

                if not bOk:
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Number of tracks {} and track order of {} don't match.".format(trackTotal, len(d)))

            except SyntaxError:
                if lstResults is None:
                    return False
                lstAnalysis.append("Command track order bad format.")
                bOk = False

        if matchExecutable:
            p = Path(matchExecutable.group(1))
            if not p.is_file():
                if lstResults is None:
                    return False
                lstAnalysis.append("mkvmerge not found - {}.".format(str(p)))
                bOk = False
            else:
                lstAnalysis.append("mkvmerge ok = {}".format(str(p)))
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("mkvmerge not found.")
            bOk = False

        if matchOutputFile:
            p = Path(matchOutputFile.group(1))
            if not Path(p.parent).is_dir():
                lstAnalysis.append("Destination directory not found - {}.".format(str(p.parent)))
                if lstResults is None:
                    return False
                bOk = False
            else:
                lstAnalysis.append("Destination directory ok = {}".format(str(p.parent)))
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Destination directory not found.")
            bOk = False

        if matchSources:
            n = 1
            for match in matchSources:
                p = Path(match.group(1))
                if not Path(p.parent).is_dir():
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Source directory {} not found {}".format(n, str(p.parent)))
                    bOk = False
                else:
                    lstAnalysis.append("Source directory {} ok = {}".format(n, str(p.parent)))

                if not Path(p).is_file():
                    print("Source bad")
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Source file {} not found {}".format(n, str(p)))
                    bOk = False
                else:
                    print("Source ok")
                    lstAnalysis.append("Source file {} ok = {}".format(n, str(p)))

                n += 1
            if n == 1:
                # if the command is so bad matchSources for loop won't run
                lstAnalysis.append("Source directory not found.")
                bOk = False
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Source directory not found.")
            bOk = False

        # This check if for optional attachments files
        n = 1
        for match in matchAttachments:
            p = Path(match.group(1))
            if not p.is_file():
                lstAnalysis.append("Attachment {} not found - {}".format(n, str(p)))
                if lstResults is None:
                    return False
                bOk = False
            else:
                lstAnalysis.append("Attachment {} ok = {}".format(n, str(p)))
            n += 1

        if lstResults is not None:
            for e in lstAnalysis:
                lstResults.append(e)

        return bOk

    @staticmethod
    def bLooksOk(strCmd, lstResults=None):
        """
        Sanity check on command any failure results in no action whatsoever
        and since the original are not modified the resulting command should be safe

        :param strCommand: command line as generated by mkvtoolnix-gui
        :type strCommand: str
        :param lstResults: list to put analysis messages
        :type lstResults: list
        :rtype: bool
        """

        if not strCmd:
            return False

        strCommand = _strStripEscapeChars(strCmd)  # Comvert line to bash style

        lstAnalysis = []

        #rg = r"^'(.*?)'\s.*?\-\-output.'(.*?)'\s.*?\s'\('\s'(.*?)'\s'\)'.*?\-\-track-order\s(.*)"  # pylint: disable=C0301
        rg = r"^'(.*?)'\s.*?\-\-output.'(.*?)'\s.*?\s'\('\s'(.*?)'\s'\)'.*?\-\-track-order\s(.*)"  # pylint: disable=C0301
        rg = r"^(.*?)\s\-\-.*?\-\-output.(.*?)\s\-\-.*?\s'\('\s(.*?)\s'\)'.*?\-\-track-order\s(.*)"

        regCommandEx = re.compile(rg)
        matchCommand = regCommandEx.match(strCommand)

        reExecutableEx = re.compile(r"^(.*?)\s\-\-")
        matchExecutable = reExecutableEx.match(strCommand)

        reOutputFileEx = re.compile(r".*?\-\-output\s(.*?)\s\-\-")
        matchOutputFile = reOutputFileEx.match(strCommand)

        reSourcesEx = re.compile(r"'\('\s(.*?)\s'\)'")
        matchSources = reSourcesEx.finditer(strCommand)

        reAttachmentsEx = re.compile(r"\-\-attach-file.(.*?)\s\-\-")
        matchAttachments = reAttachmentsEx.finditer(strCommand)

        bOk = True
        trackOrder = None
        # To look Ok must match the 5 group in the command line that
        # are expected
        # 1: mkvmerge name with fullpath
        # 2: output file
        # 3: at list one source
        # 4: track order
        if matchCommand and (len(matchCommand.groups()) == 4):
            lstAnalysis.append("Command seems ok.")
            trackOrder = matchCommand.group(4)
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Command bad format.")
            bOk = False

        if trackOrder is not None:
            try:
                d = ast.literal_eval("{" + trackOrder + "}")
                trackTotal = MKVCommand.numberOfTracks(strCommand)

                s = trackOrder.split(',')
                if trackTotal == len(s):
                    for e in s:
                        if not e.find(':') > 0:
                            bOk = False
                else:
                    bOk = False

                if not bOk:
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Number of tracks {} and track order of {} don't match.".format(trackTotal, len(d)))

            except SyntaxError:
                if lstResults is None:
                    return False
                lstAnalysis.append("Command track order bad format.")
                bOk = False

        if matchExecutable:
            f = _stripQuote(matchExecutable.group(1))
            p = Path(f)
            if not p.is_file():
                if lstResults is None:
                    return False
                lstAnalysis.append("mkvmerge not found - {}.".format(str(p)))
                bOk = False
            else:
                lstAnalysis.append("mkvmerge ok - {}".format(str(p)))
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("mkvmerge not found.")
            bOk = False

        if matchOutputFile:
            f = _stripQuote(matchOutputFile.group(1))
            p = Path(f)

            if not Path(p.parent).is_dir():
                lstAnalysis.append("Destination directory not found - {}.".format(str(p.parent)))
                if lstResults is None:
                    return False
                bOk = False
            else:
                lstAnalysis.append("Destination directory ok = {}".format(str(p.parent)))

        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Destination directory not found.")
            bOk = False

        if matchSources:
            n = 1
            for match in matchSources:
                f = _stripQuote(match.group(1))
                p = Path(f)

                if not Path(p.parent).is_dir():
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Source directory {} not found {}".format(n, str(p.parent)))
                    bOk = False
                else:
                    lstAnalysis.append("Source directory {} ok = {}".format(n, str(p.parent)))

                if not Path(p).is_file():
                    if lstResults is None:
                        return False
                    lstAnalysis.append("Source file {} not found {}".format(n, str(p)))
                    bOk = False
                else:
                    lstAnalysis.append("Source file {} ok = {}".format(n, str(p)))


                n += 1

            if n == 1:
                # if the command is so bad matchSources for loop won't run
                lstAnalysis.append("Source directory not found.")
                bOk = False
        else:
            if lstResults is None:
                return False
            lstAnalysis.append("Source directory not found.")
            bOk = False

        # This check if for optional attachments files
        n = 1
        for match in matchAttachments:
            f = _stripQuote(matchAttachments.group(1))
            p = Path(p)
            if not p.is_file():
                lstAnalysis.append("Attachment {} not found - {}".format(n, str(p)))
                if lstResults is None:
                    return False
                bOk = False
            else:
                lstAnalysis.append("Attachment {} ok = {}".format(n, str(p)))
            n += 1

        if lstResults is not None:
            for e in lstAnalysis:
                lstResults.append(e)

        return bOk

    @staticmethod
    def numberOfTracks(strCmd):
        """
        Every track have a --language option count
        them to know the number of tracks

        :param strCmd: command line
        :type strCmd: str
        :rtype: int
        """

        reLanguageEx = re.compile(r"\-\-language (.*?)\s")
        matchLanguage = reLanguageEx.findall(strCmd)

        return len(matchLanguage)

    def strCmdSourceFile(self):
        """First source file fullpath name"""

        return self._oBaseSourceFilesList[0].fullPathName if self._oBaseSourceFilesList else None

    def strCmdSourceDirectory(self):
        """First source file directory"""
        return self._oBaseSourceFilesList[0].directory if self._oBaseSourceFilesList else None

    def strCmdSourceExtension(self):
        """First source file extension"""
        return self._oBaseSourceFilesList[0].extension if self._oBaseSourceFilesList else None


class WorkFiles:
    """Files read from directories"""

    def __init__(self):

        self.baseFiles = []
        self.sourceFiles = []

    def clear(self):
        """Clear file lists"""

        self.baseFiles = []
        self.sourceFiles = []


class MKVSourceFileOld(object):
    """
    Source file properties

    :param index: index of file in the command line
    :type index: int
    :param fullPathName: filename with full path
    :type fullPathName: str
    """


    def __init__(self, index, fullPathName):
        """Use path to convert to right path OS independent"""
        fileName = Path(fullPathName)

        self.index = index
        self.fullPathName = str(fileName)
        self.directory = str(fileName.parent)
        self.extension = str(fileName.suffix)

    def __str__(self):
        return "Index: " + str(self.index) \
            + "\nName: " + self.fullPathName \
            + "\nDirectory: " + self.directory \
            + "\nExtension: " + self.extension \
            + "\n"


class MKVSourceFile(object):
    """
    Source file properties

    :param index: index of file in the command line
    :type index: int
    :param fullPathName: filename with full path
    :type fullPathName: str
    """


    def __init__(self, index, fullPathName):
        """Use path to convert to right path OS independent"""
        f = _stripQuote(fullPathName) # strip single quote adjustment for linux and macOS
        fileName = Path(f)

        self.index = index
        self.fullPathName = str(fileName)
        self.directory = str(fileName.parent)
        self.extension = str(fileName.suffix)

    def __str__(self):
        return "Index: " + str(self.index) \
            + "\nName: " + self.fullPathName \
            + "\nDirectory: " + self.directory \
            + "\nExtension: " + self.extension \
            + "\n"


def _stripQuote(strFile):
    """Strip single quote at start and end of file"""

    s = str(strFile)

    if (s[0:1] == "'") and (s[-1:] == "'"):
        s = s[1:-1]

    return s


def _strStripEscapeChars(strCommand):
    """
    Strip escape chars for the command line in the end they won't be used in a shell
    the resulting command string should work for Windows and linux
    """

    strTmp = strCommand

    if strTmp.find(r'^"^(^"') > 0:
        # This is for cmd in Windows
        strTmp = strTmp.replace('^', '').replace('/', '\\').replace('"', "'")
    elif strTmp.find(r"'\''") > 0:
        strTmp = strTmp.replace(r"'\''", "'")

    return strTmp

def _parseSourceFilesOld(strCommand, lstFileNames, dictFileNames, dictFileTokens, log=False):
    """
    In order to work with apostrophe in file names
    substitute the file names with tokens for shlex
    here parse files and create token dictionaries
    """

    regExOutput = re.compile(r".*?--output\s'(.*?)'\s--.*")
    regExSource = re.compile(r"'\('\s'(.*?)'\s'\)'")
    regExAttachFile = re.compile(r"--attach-file\s'(.*?)'\s--")
    regExTitle = re.compile(r"--title\s'(.*?)'\s--")

    fileMatch = regExOutput.match(strCommand)

    # Required Files
    if fileMatch:
        lstFileNames.append(fileMatch.group(1))
    else:
        lstFileNames = []
        return

    fileMatch = regExSource.finditer(strCommand)

    if fileMatch:

        for match in fileMatch:
            lstFileNames.append(match.group(1))
    else:
        lstFileNames = []
        return

    # Optional Files
    fileMatch = regExAttachFile.finditer(strCommand)

    for match in fileMatch:
        lstFileNames.append(match.group(1))

    fileMatch = regExTitle.finditer(strCommand)

    for match in fileMatch:
        lstFileNames.append(match.group(1))

    if lstFileNames:
        i = 0
        for strFile in lstFileNames:
            fileToken = "TOKEN!!!!!FILE{}".format(i)
            dictFileNames[fileToken] = strFile
            dictFileTokens[strFile] = fileToken
            i += 1
            if log:
                MODULELOG.debug(
                    "MC005: Token  %s - %s",
                    fileToken,
                    strFile
                )

def _parseSourceFiles(strCommand, lstFileNames, dictFileNames, dictFileTokens, log=False):
    """
    In order to work with single quote in file names
    substitute the file names with tokens for shlex
    execution the single quote break shlex split
    function

    here parse files and create token dictionaries
    """


    regExOutput = re.compile(r".*?\-\-output\s(.*?)\s\-\-.*")
    regExSource = re.compile(r"'\('\s(.*?)\s'\)'")
    regExAttachFile = re.compile(r"\-\-attach-file\s(.*?)\s\-\-")
    regExTitle = re.compile(r"--title\s(.*?)\s\-\-")

    fileMatch = regExOutput.match(strCommand)

    # Required Files
    if fileMatch:
        lstFileNames.append(fileMatch.group(1))
    else:
        lstFileNames = []
        return

    fileMatch = regExSource.finditer(strCommand)

    if fileMatch:

        for match in fileMatch:
            lstFileNames.append(match.group(1))
    else:
        lstFileNames = []
        return

    # Optional Files
    fileMatch = regExAttachFile.finditer(strCommand)

    for match in fileMatch:
        lstFileNames.append(match.group(1))

    fileMatch = regExTitle.finditer(strCommand)

    for match in fileMatch:
        lstFileNames.append(match.group(1))

    if lstFileNames:
        i = 0
        for strFile in lstFileNames:
            fileToken = "TOKEN!!!!!FILE{}".format(i)
            dictFileNames[fileToken] = strFile
            dictFileTokens[strFile] = fileToken
            i += 1
            if log:
                MODULELOG.debug(
                    "MC005: Token  %s - %s",
                    fileToken,
                    strFile
                )
