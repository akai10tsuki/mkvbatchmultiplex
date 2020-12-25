"""
Parse
"""

import colorama

from colorama import Fore, Back, Style

from pathlib import Path, PurePath


# from natsort import natsorted, ns

from vsutillib.mkv import (
    IVerifyStructure,
    MKVCommandParser
)

from adjustSources import adjustSources

from GetTracks import GetTracks
#from MKVCommandParser import MKVCommandParser

from vsutillib.macos import isMacDarkMode

# from MKVBatchMultiplex.utils import adjustSources
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
    cmd10 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01 New\Mahou Shoujo Ore - S01E01 - Magical Girl☆Transform (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:ja --default-track 1:yes '(' 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01\Mahou Shoujo Ore - S01E01 - Magical Girl☆Transform.mkv' ')' --no-audio --no-video --subtitle-tracks 2,6 --sub-charset 2:UTF-8 --language 2:en --track-name '2:English(US)' --default-track 2:yes --sub-charset 6:UTF-8 --language 6:es --track-name 6:Espanol '(' 'J:\Example\TestMedia\Example 08\[Erai-raws] Mahou Shoujo Ore\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle].mkv' ')' --track-order 0:0,0:1,1:2,1:6"

    # Out of order
    # cmd = r"'C:\Program Files\MKVToolNix\mkvmerge.exe' --ui-language en --output 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/NewFiles/Show Title - S01E02.mkv' --language 0:und --language 1:spa --default-track 1:yes '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/mkv-nosubs/Show Title ' S01E02.mkv' ')' --language 0:eng --default-track 0:yes '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/Subs/ass/ENG/Show Title - S01E02.ENG.ass' ')' --track-order 0:0,0:1,1:0"
    cmd = r"'C:\Program Files\MKVToolNix\mkvmerge.exe' --ui-language en --output 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/NewFiles/Show Title ' S01E02.mkv' --language 0:und --default-track 0:yes --display-dimensions 0:640x360 --language 1:ja --track-name '1:Original Audio' --default-track 1:yes '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/mkv/Show Title ' S01E02.mkv' ')' --language 0:en '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/mka/Show Title - S01E02.en.mka' ')' --language 0:en '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/test/subs/ENG/Show Title - S01E01.ENG.ass' ')' --track-order 0:0,0:1,1:0,2:0"
    #cmdO = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests\NewFiles\Show Title '\'' S01E02 (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:640x360 --language 1:ja --track-name '1:Original Audio' --default-track 1:yes '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests\MediaFiles\test\mkv\Show Title '\'' S01E02.mkv' ')' --language 0:en '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests\MediaFiles\test\mka\Show Title - S01E02.en.mka' ')' --language 0:en '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests\MediaFiles\test\subs\ENG\Show Title - S01E01.ENG.ass' ')' --track-order 0:0,0:1,1:0,2:0"
    # Additional audio in mka
    #cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\Dual Audio\[Kawaiika-Raws] Kyokou Suiri 01 [BDRip 1920x1080 HEVC FLAC] (1).mkv' --language 0:ja --track-name '0:BDRip by DeadNews' --default-track 0:yes --display-dimensions 0:1920x1080 --language 1:ja --track-name '1:LPCM->FLAC16' --default-track 1:yes '(' 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\[Kawaiika-Raws] Kyokou Suiri 01 [BDRip 1920x1080 HEVC FLAC].mkv' ')' --language 0:en --track-name '0:[crunchyroll]' '(' 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Sound\[Kawaiika-Raws] Kyokou Suiri 01 [BDRip 1920x1080 HEVC FLAC].eng.[crunchyroll].aac.mka' ')' --language 0:en '(' 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\[Kawaiika-Raws] Kyokou Suiri 01 [BDRip 1920x1080 HEVC FLAC].eng.[ShowY].ass' ')' --attachment-name 321impact.ttf --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\321impact.ttf' --attachment-name 'Aardvark Bold.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Aardvark Bold.ttf' --attachment-name 'Abyss TS.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Abyss TS.ttf' --attachment-name 'Aero Matics Bold.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Aero Matics Bold.ttf' --attachment-name 'Aero Matics Display Bold.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Aero Matics Display Bold.ttf' --attachment-name 'Aero Matics Display Light.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Aero Matics Display Light.ttf' --attachment-name AGaramondPro-Bold.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\AGaramondPro-Bold.otf' --attachment-name AGaramondPro-Regular.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\AGaramondPro-Regular.otf' --attachment-name brushtype-normal.ttf --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\brushtype-normal.ttf' --attachment-name 'Esperanto SemiBold.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Esperanto SemiBold.ttf' --attachment-name 'FOT Manyo Sosho Std Stripped EB.ttf' --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\FOT Manyo Sosho Std Stripped EB.ttf' --attachment-name GandhiSans-Bold.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\GandhiSans-Bold.otf' --attachment-name GandhiSans-BoldItalic.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\GandhiSans-BoldItalic.otf' --attachment-name GandhiSans-Regular.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\GandhiSans-Regular.otf' --attachment-name 'Hiragino Mincho ProN W6.otf' --attachment-mime-type application/vnd.ms-opentype --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\Hiragino Mincho ProN W6.otf' --attachment-name OpenSans-Semibold.ttf --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\OpenSans-Semibold.ttf' --attachment-name 'UVN Con Thuy.ttf' --attachment-mime-type application/x-truetype-font --attach-file 'G:\Work\[Kawaiika-Raws] (2020) Kyokou Suiri [BDRip 1920x1080 HEVC FLAC] - Text Timing\ENG Subs\fonts\UVN Con Thuy.ttf' --title 'E1 «One Eye, One Leg»' --track-order 0:0,0:1,1:0,2:0"

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

    # config.data.set(config.ConfigKey.Algorithm, 1)

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        print(f"{Fore.GREEN}Index {index} - {sourceFiles[0]}.")
        print(f"Tracks matched {iVerify.matched} unmatched {iVerify.unmatched}")
        if not iVerify:
            print(f"{Style.BRIGHT}Verification failed.{Style.RESET_ALL}")
            rc, confidence = adjustSources(oCommand, index, 1)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(f"{Fore.YELLOW}\nNew command - confidence {confidence}:\n{shellCommand}\n")
            else:
                print(f"{Fore.RED}Adjustment failed. Return code {rc} confidence {confidence}")

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True
        print()

    # config.data.set(config.ConfigKey.Algorithm, 1)

if __name__ == "__main__":
    test()
