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

from MKVBatchMultiplex.utils import adjustSources

def test():
    """
    test summary
    """
    cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 10,11 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --default-track 10:yes --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:10,0:11"
    cmd5 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"
    cmd4 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 05\Season 01\Show Title - S01E01 (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:640x360 --language 1:jpn --default-track 1:yes '(' 'J:\Example\TestMedia\Example 05\Video\Show Title - S01E01.mkv' ')' --language 0:eng '(' 'J:\Example\TestMedia\Example 05\Subs\Show Title - S01E01.ENG.ass' ')' --attachment-name Font01.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font01.otf' --attachment-name Font02.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font02.otf' --attachment-name Font03.ttf --attachment-mime-type application/x-truetype-font --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font03.ttf' --attachment-name Font04.ttf --attachment-mime-type application/x-truetype-font --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font04.ttf' --chapter-language und --chapters 'J:\Example\TestMedia\Example 05\Chapters\Show Title - S01E01 - Chapters.xml' --track-order 0:0,0:1,1:0"
    cmd6 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/NewFiles/Show Title - S01E01.mkv' --language 0:und --language 1:jpn '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/avi/Show Title - S01E01.avi' ')' --language 0:eng '(' 'C:\Projects\Python\PySide\mkvbatchmultiplex\tests/MediaFiles/Subs/ass/ENG/Show Title - S01E01.ENG.ass' ')' --track-order 0:0,0:1,1:0"
    cmd  = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 08\Mahou Shoujo Ore (2018)\Season 01\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle] (1).mkv' --subtitle-tracks 2,6 --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:und --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name '2:English(US)' --default-track 2:yes --sub-charset 6:UTF-8 --language 6:spa --track-name 6:Espanol '(' 'J:\Example\TestMedia\Example 08\[Erai-raws] Mahou Shoujo Ore\[Erai-raws] Mahou Shoujo Ore - 01 [720p][Multiple Subtitle].mkv' ')' --track-order 0:0,0:1,0:2,0:6"


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

    print()

    hasToGenerateCommands = False

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        if not iVerify:
            print(f"{Fore.GREEN}Index {index} of {sourceFiles[0]} not Ok{Style.RESET_ALL}")

            rc = adjustSources(oCommand, index)

            if rc:
                _, shellCommand = oCommand.generateCommandByIndex(index, update=True)
                print(f"New command:\n{shellCommand}\n")
            else:
                print(f"Adjustment failed.")

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True


if __name__ == "__main__":
    test()
