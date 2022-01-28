"""
Parse
"""

import platform
import pprint
import re
import shlex
from pathlib import Path, PurePath

import colorama
from colorama import Back, Fore, Style

# from MKVBatchMultiplex.utils import adjustSources
from vsutillib.macos import isMacDarkMode
from vsutillib.mkv import (
    IVerifyStructure,
    generateCommandTemplate,
    MKVAttachments,
    MKVCommandParser,
    TracksOrder,
)

from adjustSources import adjustSources
from GetTracks import GetTracks

# from MKVCommandParser import MKVCommandParser
# from commandTemplate import commandTemplate

from MKVBatchMultiplex import config

# from natsort import natsorted, ns


def test():
    """
    test summary
    """

    # This is Generate command 1 file 1, 2 and 4 should pass
    # Special characters in name
    # Missing tracks
    # Fail in second source
    # Sequential name in track name - to study how to preserve
    # Title in source - check when title is in second source
    # Tracks out of order
    cmd0 = (
        r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en "
        r"--output "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/NewFiles/"
        r"Show Title ' S01E02.mkv' "
        r"--language 0:und --track-name '0:Video Name Test 02' "
        r"--default-track 0:yes --display-dimensions 0:640x360 "
        r"--language 1:ja --track-name '1:Original Audio' --default-track 1:yes "
        r"'('"
        r" 'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/mkv/"
        r"Show Title ' S01E02.mkv' "
        r"')' "
        r"--language 0:en --track-name '0:English Track' "
        r"'('"
        r" 'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/mka/ENG/"
        r"Show Title - S01E02.en.mka' "
        r"')' "
        r"--language 0:en "
        r"'(' "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/subs/ENG/"
        r"Show Title - S01E02.ENG.ass' "
        r"')' "
        r"--attachment-name Font01.otf "
        r"--attachment-mime-type application/vnd.ms-opentype "
        r"--attach-file "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/"
        r"Attachments/Font01.otf' "
        r"--attachment-name Font02.otf "
        r"--attachment-mime-type application/vnd.ms-opentype "
        r"--attach-file "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/"
        r"Attachments/Font02.otf' "
        r"--attachment-name Font03.ttf "
        r"--attachment-mime-type application/x-truetype-font "
        r"--attach-file "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/"
        r"Attachments/Font03.ttf' "
        r"--attachment-name Font04.ttf "
        r"--attachment-mime-type application/x-truetype-font "
        r"--attach-file "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/"
        r"Attachments/Font04.ttf' "
        r"--title 'Show Title Number 2' "
        r"--chapter-language und "
        r"--chapters "
        r"'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/"
        r"chapters\Show Title - S01E01 - Chapters.xml' "
        r"--track-order 0:0,0:1,1:0,2:0"
    )

    mkvmerge = r"'C:/Program Files/MKVToolNix/mkvmerge.exe'"
    d = r"C:/Projects/Python/PySide/mkvbatchmultiplex/tests/NewFiles"
    l = r"--ui-language en"
    s = r"C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles"

    cmd = (
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

    cmd2 = (
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
        + r"--track-order 0:0,0:1,1:0,2:0,3:2"
    )

    # f = Path("./ass.xml").open(mode="wb")
    # xml = pymediainfo.MediaInfo.parse(r'J:\Example\TestMedia\Example
    # 05\Subs\Show Title - S01E01.ENG.ass', output="OLDXML")
    # f.write(xml.encode())
    # f.close()

    # return

    # g = GetTracks(f'J:\Example\TestMedia\Example 07\Source\Arte -
    # 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv')

    # print(g.mkvmerge)
    # for o in g.output:
    #    print(o.strip())

    # return

    colorama.init()

    # oAttachments = MKVAttachments()

    # template, dMatch = generateCommandTemplate(cmd, attachments=oAttachments, setTitle=True)

    # print(template)

    # return

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd
    tracksOrder = TracksOrder(oCommand.cliTracksOrder)
    templateAdjustments = TemplateAdjustments(oCommand, algorithm=1)

    # for command in oCommand.strCommands:
    #    print(command)

    # return

    # for m in dMatch[MKVParseKey.baseFilesMatch]:
    #    print(m)

    # print()
    # print(f"mkvmerge = {oCommand.mkvmerge}\n")
    # print(f"Templates {oCommand.commandTemplate}\n")
    # print(f"Output File {oCommand.cliOutputFile}")
    # print(f"Chapters File {oCommand.cliChaptersFile}")
    # print()

    # cmdTemplate = oCommand.commandTemplate
    # correctionDone = False
    # for oBaseFile in oCommand.oBaseFiles:
    #    trackOptions = oBaseFile.trackOptions

    #    print(f" Match String {oBaseFile.fullMatchString}")
    #    print(f"     Tracks = {trackOptions.tracks}")
    #    print(f"Track options {trackOptions.options}")
    #    print(f"       Tracks {trackOptions.tracks}")

    #    if trackOptions.trackNames:
    #        print(f"        Names {trackOptions.trackNames}")
    #        print(f" Track Edited {trackOptions.trackTitleEdited}")
    #        for track in trackOptions.tracks:
    #            print(f"   Name match {trackOptions.trackNameMatch(track)}")

    #    if oBaseFile.trackOptions.hasNamesToPreserve:
    #        matchString = oBaseFile.fullMatchStringWithKey()
    #        templateCorrection = oBaseFile.fullMatchStringCorrected(withKey=True)
    #        print(f"\n{matchString}\n{templateCorrection}")
    #        cmdTemplate = cmdTemplate.replace(matchString, templateCorrection, 1)
    #        if not correctionDone:
    #            correctionDone = True
    #    else:
    #        print("Nothing to see.")
    #    print()

    # if correctionDone:
    #    print(f"command form var\n{cmd}")
    #    print(f"Original Command\n{oCommand.command}")
    #    print(f"Original Template\n{oCommand.originalCommandTemplate}")
    #    print(f"New Template\n{oCommand.commandTemplate}")
    #    print(f"strCommand\n{oCommand.strCommands[3]}\nfrom template\n{oCommand.commandTemplates[3]}")
    # print()

    # for f in filesInDir:
    #    print(f)

    # print()

    # print(f"Attachment string\n{oCommand.oAttachments.attachmentsMatchString}")

    # for key in trackOptions.trackNames:
    #    print(f"Track {key} title {trackOptions.trackNames[key][1]}")
    #    print(f"Media {key} title {mediaInfo[int(key)].title}")
    #    print(
    #        f"            Are they equal? {mediaInfo[int(key)].title == trackOptions.trackNames[key][1]}"
    #    )
    #    print(f"Track {key} Modified: {trackOptions.trackTitleEdited[key]}\n")

    #    for index, mediaFile in enumerate(filesInDir):
    #        print(f"     File: {mediaFile}")
    #        trackIndex = int(key)
    #        if trackIndex < len(sources.filesMediaInfo[index]):
    #            print(
    #                f"     Track Title {sources.filesMediaInfo[index][trackIndex].title}"
    #            )
    #        else:
    #            print("     Track not found..")

    #    print()

    # pprint.pprint(oCommand.oSourceFiles.sourceFiles[0].filesInDir)

    # return

    fileIndex = 3
    oldTemplate = templateAdjustments.template(fileIndex)
    adjustedTemplate = templateAdjustments.adjustTemplate(fileIndex)
    newTemplate = templateAdjustments.templatePreserveNames(fileIndex)
    strCommand, shellCommand = oCommand.generateCommandByIndex(
        fileIndex,
        update=False,
        template=newTemplate,
        tracksOrder=templateAdjustments.adjustedTrackOrder(fileIndex),
    )
    originalTemplate = templateAdjustments.template(fileIndex)
    print(f"Old Template:\n{oldTemplate}\n\nAdjusted Template:\n{adjustedTemplate}\n")

    print(f"New Template\n{newTemplate}\n\nOriginal Template:\n{originalTemplate}")

    print(f"Command\n{strCommand}\n\nShell Command\n{shellCommand}\n")
    print(f"Command\n{oCommand.strCommands[fileIndex]}\n\nShell Command\n{oCommand.shellCommands[fileIndex]}")
    return

    hasToGenerateCommands = False

    algorithm = 1

    translations = [None] * 6
    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        print(f"{Style.DIM}{Fore.GREEN}Index {index} - {sourceFiles[0]}.")
        print(
            f"{Style.NORMAL}Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}"
        )
        if not iVerify:
            print(f"{Style.BRIGHT}{Fore.BLUE}Verification failed.{Style.RESET_ALL}")
            rc, confidence, average = adjustSources(oCommand, index, algorithm)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(
                    f"{Fore.YELLOW}\nNew command - confidence {confidence}"
                    f"-average({average}):\n{shellCommand}\n"
                )
                # Preserve
            else:
                print(
                    f"{Fore.RED}Adjustment failed. Return code {rc} confidence {confidence}"
                )

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True
        else:
            # Preserve
            pass
        print(Style.RESET_ALL)

    # for index, element in enumerate(oCommand.oBaseFiles):
    #    for fileIndex, fileName in enumerate(element.filesInDir):
    #        trackOpts = element.trackOptions
    #        translationList = oCommand.translations[fileIndex]
    #        if translationList is not None:
    #            sourceTranslation = translationList[index]
    #            if sourceTranslation is not None:
    #                trackOpts.translation = sourceTranslation
    #                print(f"For file {fileName}")
    #                print(f"Tranlation? {trackOpts.strOptions()}")
    #                print()
    #                for key in trackOpts.trackNames:
    #                    print(trackOpts.strTrackName(key))

    # print()
    # print(oCommand.originalCommandTemplate)
    # print()
    # preserveNames(oCommand)

    # for fileIndex in range(len(oCommand)):

    for shellCommand in oCommand.shellCommands:
        print(shellCommand)


def preserveNames(self):
    """
    preserveNames alter template if track names have to be preserved
    """

    originalcommandTemplate = self.originalCommandTemplate
    correctionDone = False
    optionsSrc = TemplateOptions()

    print("\n\n")
    for index, oBaseFile in enumerate(self.oSourceFiles.oBaseFiles):

        if oBaseFile.trackOptions.hasNamesToPreserve:
            trackOpts = oBaseFile.trackOptions
            matchString = oBaseFile.fullMatchStringWithKey()
            optionsSrc.index = index
            optionsSrc.trackOptions = oBaseFile.trackOptions
            for fileIndex, cmdTemplate in enumerate(self.commandTemplates):
                optionsSrc.template = cmdTemplate
                translationList = self.translations[fileIndex]
                print(f"Tlist {translationList}")
                if translationList is not None:
                    sourceTranslation = translationList[index]
                else:
                    sourceTranslation = None

                templateCorrection = oBaseFile.fullMatchStringCorrected(withKey=True)

                print(f"{optionsSrc.sourceOptions(withKey=True)}")
                print(
                    f"{optionsSrc.sourceOptionAdjusted(translation=sourceTranslation, withKey=True)}\n"
                )

                # cmdTemplate = cmdTemplate.replace(matchString, templateCorrection, 1)

                # if not correctionDone:
                #    correctionDone = True

    # if correctionDone:
    #    self.commandTemplate = cmdTemplate


class TemplateOptions:
    def __init(self, cmdTemplate=None, index=None, oCommand=None):

        self.subEx = re.compile(r"(.*?) ('\(' (.*?) '\)')")

        if cmdTemplate is not None:
            self.template = cmdTemplate

        if index is not None:
            self.index = index

    def _initVars(self):

        self.__index = None
        self.__trackOptions = None
        self.__template = None

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value

    @property
    def key(self):
        strTmp = f"<SOURCE{str(self.index)}>"
        return strTmp

    @property
    def trackOptions(self):
        return self.__trackOptions

    @trackOptions.setter
    def trackOptions(self, value):
        self.__trackOptions = value

    @property
    def template(self):
        return self.__template

    @template.setter
    def template(self, value):
        self.__template = value

    def sourceOptions(self, withKey=False):
        """
        sourceOptions options

        Args:
            withKey (bool, optional): Return options by source if True return
            string with source key. Defaults to False.

        Returns:
            str: option by source
        """
        if self.index == 0:
            regEx = r"<OUTPUTFILE>\s(.*?)\s<SOURCE0>"
        else:
            regEx = f"<SOURCE{str(self.index - 1)}>" + r"\s(.*?)\s" + self.key
            regEx.format(str(self.index - 1), str(self.index))

        strTmp = ""
        if options := re.search(regEx, self.template):
            strTmp = options.group(1)
            if withKey:
                strTmp += f" {self.key}"

        return strTmp

    def sourceOptionAdjusted(self, translation=None, withKey=False):
        """
        sourceOptionAdjusted remove track-name if not edited

        Args:
            withKey (bool, optional): If True return string with key instead of
            file string. Defaults to False.

        Returns:
            str: string with substitutions if any
        """

        if translation is not None:
            self.trackOptions.translation = translation
        strTmp = self.sourceOptions(withKey=withKey)
        for track, edited in self.trackOptions.trackTitleEdited.items():
            if not edited:
                trackName = self.trackOptions.strTrackName(track)
                strTmp = strTmp.replace(" " + trackName, "", 1)

        return strTmp

    def keySub(self):

        kSub = f"\\1 {self.key}>"
        strTmp = self.subEx.sub(kSub, self.sourceOptions)

        return strTmp


class TemplateAdjustments:
    def __init__(self, oCommand=None, algorithm=1):

        if oCommand is not None:
            self.oCommand = oCommand

        self.algorithm = algorithm

    def _initVars(self):

        self._templateOptions = TemplateOptions()
        self.__oCommand = None
        self.__templatesAdjusted = None
        self.__templatesNamesPreserved = None
        self.__translationList = None
        self.__tracksOrder = None
        self.__needAdjustment = None
        self.__rc = None
        self.__confidence = None
        self.__average = None

    @property
    def oCommand(self):
        return self.__oCommand

    @oCommand.setter
    def oCommand(self, value):

        self._initVars()
        self.__oCommand = value
        totalFiles = len(self.__oCommand)
        self.__templatesAdjusted = [None] * totalFiles
        self.__templatesNamesPreserved = [None] * totalFiles
        self.__translationList = [None] * totalFiles
        self.__tracksOrder = [None] * totalFiles
        self.__needAdjustment = [None] * totalFiles
        self.__rc = [None] * totalFiles
        self.__confidence = [None] * totalFiles
        self.__average = [None] * totalFiles

    def template(self, fileIndex):
        return self.oCommand.commandTemplates[fileIndex]

    def adjustTemplate(self, fileIndex):
        """adjust template"""

        currentTemplate = self.template(fileIndex)

        (
            rc,
            confidence,
            average,
            template,
            translationList,
            tracksOrder,
        ) = adjustSources(self.oCommand, fileIndex, self.algorithm, update=False)

        if rc:
            self.__needAdjustment[fileIndex] = True
            self.__templatesAdjusted[fileIndex] = template
            self.__translationList[fileIndex] = translationList
            self.__tracksOrder[fileIndex] = tracksOrder
            print(f"Tracks Order? {tracksOrder} info {tracksOrder.strOrder()}")

            return self.__templatesAdjusted[fileIndex]

        return currentTemplate

    def adjustedTrackOrder(self, fileIndex):
        return self.__tracksOrder[fileIndex].strOrder()

    def templatePreserveNames(self, fileIndex, useAdjusted=True):
        """
        templatePreserveNames return the template with track names removed when
        necessary

        Args:
            fileIndex (int): index of file template to adjust
        """

        template = self.template(fileIndex)

        if useAdjusted:
            isAdjusted = self.__needAdjustment[fileIndex]
            if isAdjusted:
                template = self.__templatesAdjusted[fileIndex]
                print(f"Adjusted Template on preserve\n{template}\n")

        for baseIndex, oBaseFile in enumerate(self.oCommand.oBaseFiles):

            self._templateOptions.index = baseIndex
            self._templateOptions.trackOptions = oBaseFile.trackOptions
            self._templateOptions.template = template

            if oBaseFile.trackOptions.hasNamesToPreserve:
                translationList = self.__translationList[fileIndex]
                if translationList is not None:
                    sourceTranslation = translationList[baseIndex]
                else:
                    sourceTranslation = {}

                self._templateOptions.trackOptions.translation = sourceTranslation
                option = self._templateOptions.sourceOptions(withKey=True)
                optionAdjusted = self._templateOptions.sourceOptionAdjusted(
                    withKey=True
                )
                template = template.replace(option, optionAdjusted, 1)

                print(f"Voy a bregar con for Source {baseIndex}:")
                print(
                    f"sourceTranslation\n{sourceTranslation}option\n{option}\noption adjusted\n{optionAdjusted}"
                )

        return template


if __name__ == "__main__":
    test()
