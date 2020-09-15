"""
Parse
"""

import colorama

from colorama import Fore, Back, Style

from pathlib import Path


# from natsort import natsorted, ns

from vsutillib.mkv import (
    IVerifyStructure,
    MKVCommandParser,
)

from GetTracks import GetTracks
#from MKVCommandParser import MKVCommandParser

from vsutillib.macos import isMacDarkMode

from MKVBatchMultiplex.utils import adjustSources
from MKVBatchMultiplex import config

def test():
    """
    test summary
    """
    cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 10,11 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --default-track 10:yes --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:10,0:11"
    cmd2 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"
    cmd3 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle] (1).mkv' --subtitle-tracks 2,6 --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:und --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name '2:English(US)' --default-track 2:yes --sub-charset 6:UTF-8 --language 6:spa --track-name 6:Espanol '(' 'J:\Example\TestMedia\Example 08\[Erai-raws] Mahou Shoujo Ore\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle].mkv' ')' --track-order 0:0,0:1,0:2,0:6"
    cmd4 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 09\Angelic Later (2001)\Season 01\Kidou Tenshi Angelic Layer - S01E01 (1).mkv' --no-video --language 1:jpn --default-track 1:yes --language 2:eng --sub-charset 3:UTF-8 --language 3:eng --default-track 3:yes '(' 'J:\Example\TestMedia\Example 09\Source 01\Kidou Tenshi Angelic Layer - S01E01.mkv' ')' --no-audio --no-subtitles --no-chapters --language 0:jpn --display-dimensions 0:1280x960 '(' 'J:\Example\TestMedia\Example 09\Source 02\[Kira-Fansub] Kidou Tenshi Angelic Layer ep 01v2 (BD H264 1280x960 24fps AAC) [C7E321E0].mkv' ')' --title 'Encoded By Cleo' --track-order 1:0,0:1,0:2,0:3"
    cmd5 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3,4 --subtitle-tracks 10,11 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --language 4:jpn --track-name 4:comments --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --default-track 10:yes --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:4,0:10,0:11"
    cmd6 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3,4 --subtitle-tracks 5,6,7 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --language 4:jpn --track-name 4:comments --sub-charset 5:UTF-8 --language 5:rus --track-name 5:надписи --sub-charset 6:UTF-8 --language 6:rus --track-name 6:AniLibria.tv --sub-charset 7:UTF-8 --language 7:rus --track-name '7:Yakusub Studio' '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:4,0:5,0:6,0:7"
    cmd10 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10,11 --no-chapters --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:10,0:11"
    cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mka' --audio-tracks 3 --no-video --subtitle-tracks 10 --no-chapters --language 3:jpn --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:3,0:10"
    cmd11 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mka' --audio-tracks 3 --no-video --no-subtitles --no-chapters --language 3:jpn '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')'"
    cmd8 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10 --no-chapters --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')'"
    cmd9 = r"/Applications/MKVToolNix-50.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --output '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Arte (2020)/Season 01/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10 --no-chapters --sub-charset 10:UTF-8 --language 10:en --track-name 10:ShowY '(' '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Source/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')'"
    cmd7 = r"/Applications/MKVToolNix-50.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --output '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Arte (2020)/Season 01/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10,11 --no-chapters --sub-charset 10:UTF-8 --language 10:en --track-name 10:ShowY --sub-charset 11:UTF-8 --language 11:en --track-name 11:Funimation '(' '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Source/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:10,0:11"

    #f = Path("./ass.xml").open(mode="wb")
    #xml = pymediainfo.MediaInfo.parse(r'J:\Example\TestMedia\Example 05\Subs\Show Title - S01E01.ENG.ass', output="OLDXML")
    #f.write(xml.encode())
    #f.close()

    #return

    #g = GetTracks(f'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv')

    #print(g.mkvmerge)
    #for o in g.output:
    #    print(o.strip())

    #return

    oldRegEx = [
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+).*",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\W*-\W*)(?P<title>.*)",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)"
        r"(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)"
        r"(\w*|)(\W*-\W*)(?P<title>.*?)((\W*\[.*|\W*\(.*))",
        r"(\[.*\]\W*|)(?P<name>.*?)(\W*-|)\W*(?P<episode>\d+)(\w*|)(\W*-|)(?P<title>.*).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+).*",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*)",
        r"([[(].*?[])]\W*|)(.*?)(\W*-\W*|\W*-|\W*|)(\d+)(\W*-\W*|\W*-|\W*|)(.*?)(\W*[([].*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)(?P<episode>\d+).*",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*)",
        r"([[(].*?[])]\W*|)(?P<name>.*?)(\W*-\W*|\W*-|\W*|)"
        r"(?P<episode>\d+)(\W*-\W*|\W*-|\W*|)(?P<title>.*?)(\W*[([].*)",
    ]

    for rgx in oldRegEx:
        print(rgx)

    return

    if isMacDarkMode():
        print("Yes")
    else:
        print("No")

    colorama.init()

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd

    print()

    if oCommand:
        print(f"Output extension {oCommand.outputFileExtension}")
        for cmd in oCommand.strCommands:
            print(cmd)
    else:
        print("Bummer!!")

    # return

    hasToGenerateCommands = False

    config.data.set(config.ConfigKey.Algorithm, 1)

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        if not iVerify:
            print(f"{Fore.GREEN}Index {index} - {sourceFiles[0]} not Ok")
            print(f"Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}{Style.RESET_ALL}")

            rc, confidence = adjustSources(oCommand, index)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(f"New command:\n{shellCommand}\n")
            else:
                print(f"Adjustment failed.")

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True

    config.data.set(config.ConfigKey.Algorithm, 1)

if __name__ == "__main__":
    test()
