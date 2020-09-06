""" Parser """

import ast
import pprint

# import logging
# import platform
import re

# import shlex

from pathlib import Path

# from natsort import natsorted, ns

# from vsutillib.media import MediaFileInfo
# from vsutillib.misc import XLate

from vsutillib.mkv import (
    convertToBashStyle,
    MKVAttachments,
    numberOfTracksInCommand,
    resolveOverwrite,
    stripEncaseQuotes,
    unQuote,
)

from SourceFiles import SourceFile, SourceFiles

class Parser:
    """
     Parser
    """

    def __init__(self):

        pass

    def _initVars(self):

        self.__bashCommand = None
        self.__errorFound = False
        self.__log = None
        self.__lstAnalysis = None
        self.__totalSourceFiles = None
        self.__readFiles = False
        self.__strCommand = None
        self.__shellCommands = []
        self.__strCommands = []

        self.cliChaptersFile = None
        self.cliChaptersFileMatchString = None
        self.chaptersLanguage = None
        self.commandTemplate = None
        self.language = None
        self.mkvmerge = None
        self.mkvpropedit = None
        self.cliOutputFile = None
        self.cliOutputFileMatchString = None
        self.cliTitleMatchString = None
        self.cliTrackOrder = None

        self.chaptersFiles = []
        self.filesInDirByKey = {}
        self.dirsByKey = {}
        self.titles = []

        self.oAttachments = MKVAttachments()
        self.oFiles = []
        self.oSourceFiles = SourceFiles()

    @property
    def command(self):
        return self.__strCommand

    @command.setter
    def command(self, value):
        if isinstance(value, str):
            self._initVars()
            # self.__strCommand = value

            self.__strCommand = removeTitle(value)

            strCommand = convertToBashStyle(self.__strCommand)

            self.__bashCommand = strCommand
            self._parse()
            # self.__readFiles = True

    def _parse(self):
        """
        _parse parse command line
        """

        strCommand = self.__bashCommand
        self.__lstAnalysis = []

        rg = r"^(.*?)\s--.*?--output.(.*?)\s--.*?\s'\('\s(.*?)\s'\)'.*?--track-order\s(.*)"

        reCommandEx = re.compile(rg)
        reExecutableEx = re.compile(r"^(.*?)\s--")
        reLanguageEx = re.compile(r"--ui-language (.*?) --")
        reOutputFileEx = re.compile(r".*?--output\s(.*?)\s--")

        reFilesEx = re.compile(
            (
                r"(?=--audio-tracks "
                r"|--video-tracks "
                r"|--subtitle-tracks "
                r"|--button-tracks "
                r"|--track-tags  "
                r"|--attachments "
                r"|--no-audio "
                r"|--no-video "
                r"|--no-subtitles "
                r"|--no-buttons "
                r"|--no-track-tags "
                r"|--no-chapters "
                r"|--no-global-tags "
                r"|--chapter-charset "
                r"|--chapter-language "
                r"|--language "
                r")"
                r"(.*?) '\(' (.*?) '\)'"
            )
        )
        reChaptersFileEx = re.compile(
            r"--chapter-language (.*?) --chapters (.*?) (?=--)"
        )
        self.__errorFound = False

        # To look Ok must match the 4 expected groups in the
        # command line
        # 1: mkvmerge name with fullpath
        # 2: output file
        # 3: at list one source
        # 4: track order
        if (matchCommand := reCommandEx.match(strCommand)) and (
            len(matchCommand.groups()) == 4  # pylint: disable=used-before-assignment
        ):
            self.cliTrackOrder = matchCommand.group(4)
            self.__lstAnalysis.append("chk: Command seems ok.")
            try:
                d = ast.literal_eval("{" + self.cliTrackOrder + "}")
                trackTotal = numberOfTracksInCommand(strCommand)
                s = self.cliTrackOrder.split(",")
                if trackTotal == len(s):
                    for e in s:
                        if not e.find(":") > 0:
                            self.__errorFound = True
                else:
                    self.__errorFound = True
                if self.__errorFound:
                    self.__lstAnalysis.append(
                        "err: Number of tracks {} and track order of {} don't match.".format(
                            trackTotal, len(d)
                        )
                    )
            except SyntaxError:
                self.__lstAnalysis.append("err: Command track order bad format.")
                self.__errorFound = True
        else:
            self.__lstAnalysis.append("err: Command bad format.")
            self.__errorFound = True

        if matchUILanguage := reLanguageEx.search(strCommand):
            self.language = matchUILanguage.group(1)

        if matchExecutable := reExecutableEx.match(strCommand):
            f = stripEncaseQuotes(matchExecutable.group(1))
            p = Path(f)
            try:
                test = p.is_file()
            except OSError:
                self.__lstAnalysis.append(
                    "err: mkvmerge incorrect syntax - {}.".format(str(p))
                )
                self.__errorFound = True
            else:
                if test:
                    self.mkvmerge = p
                    self.mkvpropedit = str(p.parent) + "mkvpropedit.exe"
                    self.__lstAnalysis.append("chk: mkvmerge ok - {}.".format(str(p)))
                else:
                    self.__lstAnalysis.append(
                        "err: mkvmerge not found - {}.".format(str(p))
                    )
                    self.__errorFound = True
        else:
            self.__lstAnalysis.append("err: mkvmerge not found.")
            self.__errorFound = True

        if matchOutputFile := reOutputFileEx.match(strCommand):
            self.cliOutputFile = None
            self.cliOutputFileMatchString = None
            f = stripEncaseQuotes(matchOutputFile.group(1))
            f = f.replace(r"'\''", "'")
            p = Path(f)
            try:
                test = Path(p.parent).is_dir()
            except OSError:
                self.__errorFound = True
                self.__lstAnalysis.append(
                    "err: Destination directory incorrect syntax - {}.".format(
                        str(p.parent)
                    )
                )
            else:
                if test:
                    self.cliOutputFile = p
                    self.cliOutputFileMatchString = matchOutputFile.group(1)
                    self.__lstAnalysis.append(
                        "chk: Destination directory ok = {}.".format(str(p.parent))
                    )
                else:
                    self.__errorFound = True
                    self.__lstAnalysis.append(
                        "err: Destination directory not found - {}.".format(
                            str(p.parent)
                        )
                    )
        else:
            self.__errorFound = True
            self.__lstAnalysis.append("err: No output file found in command.")

        if matchFiles := reFilesEx.finditer(strCommand):
            for index, match in enumerate(matchFiles):
                oFile = SourceFile(match.group(0))
                if oFile:
                    self.oFiles.append(oFile)
                    self.oSourceFiles.append(oFile)
                    if self.__totalSourceFiles is None:
                        self.__totalSourceFiles = len(oFile.filesInDir)
                    self.__lstAnalysis.append(
                        "chk: Source directory ok - {}.".format(
                            str(oFile.fileName.parent)
                        )
                    )
                    if index == 0:
                        self.filesInDirByKey[MKVParseKey.outputFile] = []
                        self.dirsByKey[MKVParseKey.outputFile] = ""
                        for f in oFile.filesInDir:
                            if self.dirsByKey[MKVParseKey.outputFile] == "":
                                self.dirsByKey[
                                    MKVParseKey.outputFile
                                ] = oFile.fileName.parent

                            of = self.cliOutputFile.parent.joinpath(f.stem + ".mkv")
                            of = resolveOverwrite(of)
                            self.filesInDirByKey[MKVParseKey.outputFile].append(of)
                    key = "<SOURCE{}>".format(str(index))
                    self.filesInDirByKey[key] = oFile.filesInDir
                    self.dirsByKey[key] = oFile.fileName.parent
                    if len(oFile.filesInDir) != self.__totalSourceFiles:
                        self.__errorFound = True
                        self.__lstAnalysis.append(
                            "err: Error source files TOTAL mismatched." + match.group(0)
                        )
                else:
                    self.__errorFound = True
                    self.__lstAnalysis.append(
                        "err: Error reading source files." + match.group(2)
                    )
        else:
            self.__errorFound = True
            self.__lstAnalysis.append("err: No source file found in command.")

        #
        # Optional
        #
        if matchChaptersFile := reChaptersFileEx.search(strCommand):
            self.chaptersLanguage = matchChaptersFile.group(1)
            self.cliChaptersFile = None
            self.cliChaptersFileMatchString = None
            f = unQuote(matchChaptersFile.group(2))
            p = Path(f)
            try:
                test = p.is_file()
            except OSError:
                self.__lstAnalysis.append(
                    "err: Chapters file incorrect syntax - {}.".format(str(p))
                )
                self.__errorFound = True
            else:
                if test:
                    self.cliChaptersFile = p
                    self.cliChaptersFileMatchString = matchChaptersFile.group(2)
                    self.__lstAnalysis.append(
                        "chk: Chapters file ok - {}.".format(str(p.parent))
                    )
                else:
                    self.__lstAnalysis.append(
                        "chk: Chapters file not found - {}.".format(str(p.parent))
                    )
                    self.__errorFound = True

        if self.__errorFound:
            self.__readFiles = True

class MKVParseKey:

    attachmentFiles = "<ATTACHMENTS>  "
    chaptersFile = "<CHAPTERS>"
    outputFile = "<OUTPUTFILE>"
    title = "<TITLE>"

def removeTitle(strCommand):
    """
    _removeTitle remove --title option from command
    """

    strTmp = strCommand

    reTitleEx = re.compile(r".*?--title\s(.*?)\s--")

    if matchTitle := reTitleEx.match(strCommand):
        cliTitleMatchString = matchTitle.group(1)

        strTmp = strTmp.replace("--title " + cliTitleMatchString + " ", "", 1)

    return str(strTmp)
