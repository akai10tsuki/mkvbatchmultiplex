"""
Parse
"""

import pprint

import colorama

from colorama import Fore, Back, Style

from pathlib import Path, PurePath


# from natsort import natsorted, ns

from vsutillib.mkv import IVerifyStructure

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
        r"'C:\Program Files\MKVToolNix\mkvmerge.exe' --ui-language en "
        r"--output "
        r"'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/NewFiles/"
        r"Show Title ' S01E02.mkv' "
        r"--language 0:und --track-name '0:Video Name Test 02' "
        r"--default-track 0:yes --display-dimensions 0:640x360 "
        r"--language 1:ja --track-name '1:Original Audio' --default-track 1:yes "
        r"'('"
        r" 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/mkv/"
        r"Show Title ' S01E02.mkv' "
        r"')' "
        r"--language 0:en --track-name '0:English Track' "
        r"'('"
        r" 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/mka/"
        r"Show Title - S01E02.en.mka' "
        r"')' "
        r"--language 0:en "
        r"'(' "
        r"'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/subs/ENG/"
        r"Show Title - S01E02.ENG.ass' "
        r"')' "
        r"--title 'Show Title Number 2' "
        r"--track-order 0:0,0:1,1:0,2:0")

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

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd

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
                print(f"     Track Title {sources.filesMediaInfo[index][trackIndex].title}")
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


if __name__ == "__main__":
    test()
