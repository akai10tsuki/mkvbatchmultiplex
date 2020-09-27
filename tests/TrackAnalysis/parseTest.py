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
    cmdt = r"'C:\Program Files\MKVToolNix\mkvmerge.exe' --ui-language en --output 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/NewFiles/Show Title - S01E01.mkv' --language 0:und --language 1:jpn '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/avi/Show Title - S01E01.avi' ')' --language 0:eng '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/Subs/ass/ENG/Show Title - S01E01.ENG.ass' ')' --track-order 0:0,0:1,1:0"

    # Example 07 Arte
    cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 8,9 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:ja --default-track 3:yes --sub-charset 8:UTF-8 --language 8:en --track-name 8:ShowY --default-track 8:yes --sub-charset 9:UTF-8 --language 9:en --track-name 9:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:8,0:9"
    # Example 06 Key the Metal Idol
    cmd2 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 06\Season 01 New\[Koten_Gars] Key The Metal Idol OVA - 01 [DVD][Hi10][480p][AC3+FLAC] [9A65FECD] (1).mkv' --language 0:ja --track-name '0:Episode 01 - Startup' --default-track 0:yes --display-dimensions 0:708x531 --language 1:en --track-name '1:AC3 2.0 [R1 Discotek-DVD]' --language 2:ja --track-name '2:LPCM 2.0 [R2J DVD]' --default-track 2:yes --sub-charset 3:UTF-8 --language 3:en --track-name 3:Signs --default-track 3:yes --sub-charset 4:UTF-8 --language 4:en --track-name 4:Dialogue '(' 'J:\Example\TestMedia\Example 06\Season 01\[Koten_Gars] Key The Metal Idol OVA - 01 [DVD][Hi10][480p][AC3+FLAC] [9A65FECD].mkv' ')' --title 'Key the Metal Idol Episode 01 - Startup' --track-order 0:0,0:2,0:1,0:4,0:3"

    # Example 07 Arte MacOS
    cmd9 = r"/Applications/MKVToolNix-50.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --output '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Arte (2020)/Season 01/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10 --no-chapters --sub-charset 10:UTF-8 --language 10:en --track-name 10:ShowY '(' '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Source/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')'"
    cmd7 = r"/Applications/MKVToolNix-50.0.0.app/Contents/MacOS/mkvmerge --ui-language en_US --output '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Arte (2020)/Season 01/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mks' --no-audio --no-video --subtitle-tracks 10,11 --no-chapters --sub-charset 10:UTF-8 --language 10:en --track-name 10:ShowY --sub-charset 11:UTF-8 --language 11:en --track-name 11:Funimation '(' '/Volumes/Plex-Media 2 T/Example/TestMedia/Example 07/Source/Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:10,0:11"

    # Example 08 Mahou Shoujo Ore
    cmd3 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle] (1).mkv' --no-subtitles --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:und --default-track 1:yes '(' 'J:\Example\TestMedia\Example 08\[Erai-raws] Mahou Shoujo Ore\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle].mkv' ')' --track-order 0:0,0:1"
    cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01 New\Mahou Shoujo Ore - S01E01 - Magical Girl☆Transform (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:ja --default-track 1:yes '(' 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01\Mahou Shoujo Ore - S01E01 - Magical Girl☆Transform.mkv' ')' --no-audio --no-video --subtitle-tracks 2,6 --sub-charset 2:UTF-8 --language 2:en --track-name '2:English(US)' --default-track 2:yes --sub-charset 6:UTF-8 --language 6:es --track-name 6:Espanol '(' 'J:\Example\TestMedia\Example 08\[Erai-raws] Mahou Shoujo Ore\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle].mkv' ')' --track-order 0:0,0:1,1:2,1:6"
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

    colorama.init()

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd

    #trackOptions = oCommand.oSourceFiles.sourceFiles[0].trackOptions
    #mediaInfo = oCommand.oSourceFiles.sourceFiles[0].trackOptions.mediaInfo

    #for key in trackOptions.trackNames:
    #    print(f"Track {key} title {trackOptions.trackNames[key][1]}")
    #    print(f"Media {key} title {mediaInfo[int(key)].title}")
    #    print(f"Are they equal? {mediaInfo[int(key)].title == trackOptions.trackNames[key][1]}")
    #    print(f"Track {key} Modified: {trackOptions.trackTitleEdited[key]}\n")

    #print(oCommand.oSourceFiles.sourceFiles[0].filesInDir)

    #return

    hasToGenerateCommands = False

    config.data.set(config.ConfigKey.Algorithm, 1)

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        print(f"{Fore.GREEN}Index {index} - {sourceFiles[0]} not Ok")
        print(f"Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}{Style.RESET_ALL}")
        if not iVerify:
            rc, confidence = adjustSources(oCommand, index)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(f"New command - confidence {confidence}:\n{shellCommand}\n")
            else:
                print(f"Adjustment failed.")

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True

    config.data.set(config.ConfigKey.Algorithm, 1)

if __name__ == "__main__":
    test()
