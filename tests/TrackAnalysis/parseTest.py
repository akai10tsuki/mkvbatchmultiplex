"""
Parse
"""

import ast
import copy
import pprint

# import logging
# import platform
import re

import shlex

import colorama

from colorama import Fore, Back, Style

from pathlib import Path

import pymediainfo

# from natsort import natsorted, ns

from vsutillib.media import MediaFileInfo
from vsutillib.mkv import (
    MergeOptions,
    TrackOptions,
    MKVCommandParser,
    generateCommand,
)


from vsutillib.misc import XLate, iso639


# from mkvcommandparser import MKVCommandParser
# from TrackOptions import TrackOptions
from IVerifyStructure import IVerifyStructure
#from iso639 import iso639

# from MergeOptions import MergeOptions
# from MediaFileInfo import MediaFileInfo
from findSimilarTrack import findSimilarTrack

from TracksOrder import TracksOrder

from adjustSources import adjustSources

def test():
    """
    test summary
    """
    cmd0 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\Series Title (2017)\Season 01\Episode - S01E03 (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:jpn --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng '(' 'J:\Example\Series Title (2017)\Season 01\Episode - S01E03.mkv' ')' --no-audio --no-video --sub-charset 2:UTF-8 --language 2:ita --track-name 2:Italian --default-track 2:yes '(' 'J:\Example\Series Title (2017)\New Sub\Episode (Italian Subs) - S01E03.mkv' ')' --title 'Episode 01' --track-order 0:0,0:1,1:2,0:2"
    cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 10,11 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --default-track 10:yes --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:10,0:11"
    cmd2 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"
    cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name '9:ShowY \/'\' --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"
    cmd3 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 8,9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 8:UTF-8 --language 8:ara --track-name 8:Athbul-Khayal --sub-charset 9:UTF-8 --language 9:eng --track-name '9:ShowY Translation' --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:8,0:9,0:10"
    cmd4 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'J:\Example\TestMedia\Example 05\Season 01\Show Title - S01E01 (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:640x360 --language 1:jpn --default-track 1:yes '(' 'J:\Example\TestMedia\Example 05\Video\Show Title - S01E01.mkv' ')' --language 0:eng '(' 'J:\Example\TestMedia\Example 05\Subs\Show Title - S01E01.ENG.ass' ')' --attachment-name Font01.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font01.otf' --attachment-name Font02.otf --attachment-mime-type application/vnd.ms-opentype --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font02.otf' --attachment-name Font03.ttf --attachment-mime-type application/x-truetype-font --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font03.ttf' --attachment-name Font04.ttf --attachment-mime-type application/x-truetype-font --attach-file 'J:\Example\TestMedia\Example 05\Attachments\Show Title - S01E01\Font04.ttf' --chapter-language und --chapters 'J:\Example\TestMedia\Example 05\Chapters\Show Title - S01E01 - Chapters.xml' --track-order 0:0,0:1,1:0"
    option = r"--language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:jpn --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng"
    option2 = r"--no-audio --no-video --sub-charset 2:UTF-8 --language 2:ita --track-name 2:Italian --default-track 2:yes"

    """
    'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en
    --output 'J:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv'
    --audio-tracks 3 --subtitle-tracks 9,10
    --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080
    --language 3:jpn --default-track 3:yes
    --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes
    --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation
    '(' 'J:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"

    --audio-tracks 3 --subtitle-tracks 9,10
    --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080
    --language 3:jpn --default-track 3:yes
    --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes
    --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation

    --audio-tracks 3--subtitle-tracks 9,10
    --language 0:und--default-track 0:yes--display-dimensions 0:1920x1080
    --language 3:jpn--default-track 3:yes
    --sub-charset 9:UTF-8--language 9:eng--track-name 9:ShowY--default-track 9:yes
    --sub-charset 10:UTF-8--language 10:eng--track-name 10:Funimation

    --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation

    --track-name '9:ShowY \/'\'

    --track-name 9:ShowY \/'

    """

    # opts = TrackOptions()
    # opts.options = option2

    # for o in opts.aOptions:
    #    print(o)

    # print(opts.optionsByTrack('0'))

    # print(f"Tracks {opts.tracks}")
    # print(f"Options {opts.options}")
    # print(f"Options {opts.strOptions()}")
    # opts.translation = {'2': '3'}
    # print(f"Options {opts.strOptions()}")

    colorama.init()

    iVerify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd
    # mOptions = MergeOptions()
    # trackOptions = oCommand.oBaseFiles[0].trackOptions
    # mediaInfo = oCommand.oBaseFiles[0].mediaFileInfo


    # print(trackOptions.strIOptions)
    #print(trackOptions.parsedIOptions)
    #print(trackOptions.optionsByTrack())
    # template = oCommand.commandTemplates[0]
    # trackOptions.translation = {"9": "10", "10": "11"}
    # print(f"Track Order {oCommand.cliTracksOrder}")
    # print(f"Template: {template}")
    # print(
    #    f"Translation: {trackOptions.translation} "
    #    f"Order Translation: {trackOptions.orderTranslation}"
    # )
    # print(f"Shell Command: {oCommand.shellCommands[0]}")


    # trkOptions = TrackOptions()
    # trkOptions.options = "--no-global-tags " + trackOptions.options
    # print(f"  sOptions: {trkOptions.strIOptions}")
    # print(f" saOptions: {trkOptions.parsedIOptions}")
    # print(f"  Original: {trkOptions.strOptions({'9': '10', '10': '11'})}")
    # print(trackOptions.tracks)
    # trackOptions.translation = {"9": "10", "10": "11"}
    # print(f"  Original: {trackOptions.options}")
    # print(f"Translated: {trackOptions.strOptions()}")

    print()

    hasToGenerateCommands = False

    for index, sourceFiles in enumerate(oCommand.oSourceFiles):
        iVerify.verifyStructure(oCommand, index)
        if not iVerify:
            print(f"{Fore.GREEN}Index {index} of {sourceFiles[0]} not Ok{Style.RESET_ALL}")

            rc = adjustSources(oCommand, index)

            if not hasToGenerateCommands and rc:
                hasToGenerateCommands = True

    if hasToGenerateCommands:
        oCommand.generateCommands()

        for cmd in oCommand.shellCommands:
            print(cmd)


    # print(f"        Order: {oCommand.oBaseFiles[0].fileOrder}")
    # print(f"       Tracks: {trackOptions.tracks}")
    # print(f"        Names: {trackOptions.trackNames}")
    # print(f"      Options: {trackOptions.aOptions}")
    # print(f"       Medida: \n\n{oCommand.oBaseFiles[0].mediaFileInfo}")
    # print(f" Sum Trk Type: \n\n{oCommand.oBaseFiles[0].mediaFileInfo.totalTracksByType}")

    # Track ID 0: video (MPEG-H/HEVC/H.265)
    # Track ID 1: audio (AAC)
    # Track ID 2: audio (AAC)
    # Track ID 3: audio (FLAC)
    # Track ID 4: audio (FLAC)
    # Track ID 5: subtitles (SubStationAlpha)
    # Track ID 6: subtitles (SubStationAlpha)
    # Track ID 7: subtitles (SubStationAlpha)
    # Track ID 8: subtitles (SubStationAlpha)
    # Track ID 9: subtitles (SubStationAlpha)
    # Track ID 10: subtitles (SubStationAlpha)
    # Track ID 11: subtitles (SubStationAlpha)

    # for track in mediaInfo.mediaInfo.tracks:
    #    if track.track_type == "General":
    #        print(f"      General: {track.codec}")
    #        print(f"       Format: {track.format}")
    #        print(f"        Title: {track.title}")
    #        print(f"Video Streams: {track.count_of_video_streams}")
    #        print(f"Audio Streams: {track.count_of_audio_streams}")
    #        print(f" Text Streams: {track.count_of_text_streams}")
    #        print(f"  Attachments: {track.attachments.split(' / ')}")
    #        print(f"     Duration: {track.duration}")

    # if track.track_type in ("Video", "Audio", "Text"):
    #    print(f"Track ID {track.streamorder}: Type Order {track.stream_identifier} {track.track_type} ({track.format})")

    # if track.track_type == "Menu":
    #    print("Menu", track.__dict__)

    # if track.track_type in ("Video", "Audio", "Text"):
    #    self.totalTracksByType[track.track_type] += 1
    #    self.__lstMediaTracks.append(
    #        MediaTrackInfo(
    #            track.streamorder,
    #            track.track_type,
    #            iso639(track.language, codeOnly=True),
    #            track.default,
    #            track.forced,
    #            track.title,
    #            track.codec,
    #            track.format,
    #        )
    #    )

    # f = Path("./json.json").open(mode="wb")
    # xml = pymediainfo.MediaInfo.parse(r'J:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv', output="JSON")
    # f.write(xml.encode())
    # f.close()

    # for t in mediaInfo:
    #    print(t)


    # for trk in sTracks:
    #    print(f"{trk}")
    # Separate Options Exactly


if __name__ == "__main__":
    test()
