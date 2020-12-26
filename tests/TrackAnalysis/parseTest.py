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
)

from adjustSources import adjustSources
from GetTracks import GetTracks

# from MKVCommandParser import MKVCommandParser
#from commandTemplate import commandTemplate

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

    #oAttachments = MKVAttachments()

    #template, dMatch = generateCommandTemplate(cmd, attachments=oAttachments, setTitle=True)

    #print(template)

    #return

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd

    # for m in dMatch[MKVParseKey.baseFilesMatch]:
    #    print(m)

    #print()
    #print(f"mkvmerge = {oCommand.mkvmerge}\n")
    #print(f"Templates {oCommand.commandTemplate}\n")
    #print(f"Output File {oCommand.cliOutputFile}")
    #print(f"Chapters File {oCommand.cliChaptersFile}")
    #print()

    #trackOptions = oCommand.oSourceFiles.sourceFiles[0].trackOptions
    #mediaInfo = oCommand.oSourceFiles.sourceFiles[0].trackOptions.mediaInfo
    #filesInDir = oCommand.oSourceFiles.sourceFiles[0].filesInDir
    #sources = oCommand.oSourceFiles.sourceFiles[0]

    #print(f"Tracks = {trackOptions.tracks}\n")

    #print(f"Track options {trackOptions.options}")
    #print(f"Tracks {trackOptions.tracks}")
    #print(f"Names {trackOptions.trackNames}")
    #print(f"Track Edited {trackOptions.trackTitleEdited}")
    #for track in trackOptions.tracks:
    #    print(f"Name match {trackOptions.trackNameMatch(track)}")
    #for f in filesInDir:
    #    print(f)

    #print()

    #print(f"Attachment string\n{oCommand.oAttachments.attachmentsMatchString}")

    #for key in trackOptions.trackNames:
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

    #pprint.pprint(oCommand.oSourceFiles.sourceFiles[0].filesInDir)

    #return

    hasToGenerateCommands = False

    algorithm = 1

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        print(f"{Style.DIM}{Fore.GREEN}Index {index} - {sourceFiles[0]}.")
        print(f"{Style.NORMAL}Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}")
        if not iVerify:
            print(f"{Style.BRIGHT}{Fore.BLUE}Verification failed.{Style.RESET_ALL}")
            rc, confidence, average = adjustSources(oCommand, index, algorithm)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(
                    f"{Fore.YELLOW}\nNew command - confidence {confidence}"
                    f"-average({average}):\n{shellCommand}\n"
                )
            else:
                print(
                    f"{Fore.RED}Adjustment failed. Return code {rc} confidence {confidence}"
                )

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True
        print()


class MKVParseKeyCarajo:

    attachmentFiles = "<ATTACHMENTS>"
    chaptersFile = "<CHAPTERS>"
    outputFile = "<OUTPUTFILE>"
    title = "<TITLE>"
    trackOrder = "<ORDER>"
    mkvmergeMatch = "mkvmergeMatch"
    outputMatch = "outputMatch"
    baseFilesMatch = "baseFilesMatch"
    chaptersMatch = "chaptersMatch"


if __name__ == "__main__":
    test()
