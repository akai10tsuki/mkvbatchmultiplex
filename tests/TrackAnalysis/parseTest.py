"""
Parse
"""

import platform
import pprint
import re
import shlex

import colorama

from colorama import Fore, Back, Style

from pathlib import Path, PurePath


# from natsort import natsorted, ns

from vsutillib.mkv import IVerifyStructure, MKVAttachments, stripEncaseQuotes

from adjustSources import adjustSources

from GetTracks import GetTracks
from MKVCommandParser import MKVCommandParser

from vsutillib.macos import isMacDarkMode

# from MKVBatchMultiplex.utils import adjustSources
from MKVBatchMultiplex import config


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
    cmd = (
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
        r" 'C:/Projects/Python/PySide/mkvbatchmultiplex/tests/MediaFiles/test/mka/"
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

    fTemplate = _template(cmd, hasTitle=True)

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd

    print(f"Template = {fTemplate}\n")
    print(f"Template = {oCommand.commandTemplate}\n")

    return

    trackOptions = oCommand.oSourceFiles.sourceFiles[0].trackOptions
    mediaInfo = oCommand.oSourceFiles.sourceFiles[0].trackOptions.mediaInfo
    filesInDir = oCommand.oSourceFiles.sourceFiles[0].filesInDir
    sources = oCommand.oSourceFiles.sourceFiles[0]

    print(f"Tracks = {trackOptions.tracks}\n")
    print(f"Template = {oCommand.commandTemplate}\n")

    print(f"Track options {trackOptions.options}")
    print(f"Tracks {trackOptions.tracks}")
    print(f"Names {trackOptions.trackNames}")
    print(f"Track Edited {trackOptions.trackTitleEdited}")
    for track in trackOptions.tracks:
        print(f"Name match {trackOptions.trackNameMatch(track)}")

    return

    for key in trackOptions.trackNames:
        print(f"Track {key} title {trackOptions.trackNames[key][1]}")
        print(f"Media {key} title {mediaInfo[int(key)].title}")
        print(
            f"            Are they equal? {mediaInfo[int(key)].title == trackOptions.trackNames[key][1]}"
        )
        print(f"Track {key} Modified: {trackOptions.trackTitleEdited[key]}\n")

        for index, mediaFile in enumerate(filesInDir):
            print(f"     File: {mediaFile}")
            trackIndex = int(key)
            if trackIndex < len(sources.filesMediaInfo[index]):
                print(
                    f"     Track Title {sources.filesMediaInfo[index][trackIndex].title}"
                )
            else:
                print("     Track not found..")

        print()

    pprint.pprint(oCommand.oSourceFiles.sourceFiles[0].filesInDir)

    return

    hasToGenerateCommands = False

    algorithm = 1

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        print(f"{Fore.GREEN}Index {index} - {sourceFiles[0]}.")
        print(f"Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}")
        if not iVerify:
            print(f"{Style.BRIGHT}Verification failed.{Style.RESET_ALL}")
            rc, confidence = adjustSources(oCommand, index, 1)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(
                    f"{Fore.YELLOW}\nNew command - confidence {confidence}:\n{shellCommand}\n"
                )
            else:
                print(
                    f"{Fore.RED}Adjustment failed. Return code {rc} confidence {confidence}"
                )

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True
        print()

    # config.data.set(config.ConfigKey.Algorithm, 1)


def _template(bashCommand, hasTitle=False):

    cmdTemplate = bashCommand

    reExecutableEx = re.compile(r"^(.*?)\s--")
    reOutputFileEx = re.compile(r".*?--output\s(.*?)\s--")
    reFilesEx = re.compile(r"'\(' (.*?) '\)'")
    reChaptersFileEx = re.compile(r"--chapter-language (.*?) --chapters (.*?) (?=--)")
    reTracksOrderEx = re.compile(r"--track-order\s(.*)")
    reTitleEx = re.compile(r"--title\s(.*?)(?=$|\s--)")

    if matchExecutable := reExecutableEx.match(cmdTemplate):
        m = matchExecutable.group(1)
        f = stripEncaseQuotes(m)
        e = shlex.quote(f)

        ##
        # BUG 1
        # Reported by zFerry98
        #
        # When running in Windows there is no space in the mkvmerge executable path
        # \ is use as escape
        # Command: ['C:binmkvtoolnixmkvmerge.exe', ...
        #
        # Solution:
        #   Force quotes for mkvmerge executable
        #
        #   Command: ['C:\\bin\\mkvtoolnix\\mkvmerge.exe'
        ##
        if platform.system() == "Windows":
            if e[0:1] != "'":
                e = "'" + f + "'"
        ##

        step = 0
        cmdTemplate = bashCommand
        #print(f"Template Step {step}\n{cmdTemplate}\n")
        cmdTemplate = cmdTemplate.replace(m, e, 1)
        step += 1
        #print(f"Template Quotes for Executable Step {step}\n{cmdTemplate}\n")

        if matchOutputFile := reOutputFileEx.match(bashCommand):
            matchString = matchOutputFile.group(1)
            cmdTemplate = cmdTemplate.replace(matchString, MKVParseKey.outputFile, 1)
            step += 1
            #print(f"Template OutputFile Step {step}\n{cmdTemplate}\n")

        if matchFiles := reFilesEx.finditer(bashCommand):
            for index, match in enumerate(matchFiles):
                matchString = match.group(0)
                key = "<SOURCE{}>".format(str(index))
                cmdTemplate = cmdTemplate.replace(matchString, key, 1)
            step += 1
            #print(f"Template {key} Step {step}\n{cmdTemplate}\n")

        oAttachments = MKVAttachments()
        oAttachments.strCommand = bashCommand

        if oAttachments.cmdLineAttachments:
            cmdTemplate = cmdTemplate.replace(
                oAttachments.attachmentsMatchString,
                MKVParseKey.attachmentFiles,
                1,
            )
            step += 1
            #print(f"Template attachments {step}\n{cmdTemplate}\n")

        ##
        # Bug #3
        #
        # It was not preserving the episode title
        #
        # Remove title before parsing and added the <TITLE> key to the template
        # If there is no title read --title '' will be used.
        # working with \ ' " backslash, single and double quotes in same title
        ##

        # Add title to template

        if match := reChaptersFileEx.search(bashCommand):
            matchString = match.group(2)
            cmdTemplate = cmdTemplate.replace(matchString, MKVParseKey.chaptersFile, 1)
            step += 1
            #print(f"Template Chapters Step {step} {cmdTemplate}\n")

        if hasTitle:
            if match := reTitleEx.search(bashCommand):
                matchString = match.group(1)
                cmdTemplate = cmdTemplate.replace(
                    matchString,
                    MKVParseKey.title,
                    1,
                )
            else:
                cmdTemplate += "--title " + MKVParseKey.title

            step += 1
            #print(f"Template Title Step {step}\n{cmdTemplate}\n")

        if match := reTracksOrderEx.search(bashCommand):
            matchString = match.group(1)
            cmdTemplate = cmdTemplate.replace(matchString, MKVParseKey.trackOrder, 1)
            step += 1
            #print(f"Template Step {step} {cmdTemplate}\n")

    return cmdTemplate
class MKVParseKey:

    attachmentFiles = "<ATTACHMENTS>"
    chaptersFile = "<CHAPTERS>"
    outputFile = "<OUTPUTFILE>"
    title = "<TITLE>"
    trackOrder = "<ORDER>"


if __name__ == "__main__":
    test()
