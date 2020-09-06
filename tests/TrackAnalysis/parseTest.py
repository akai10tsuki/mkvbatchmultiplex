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

# from vsutillib.media import MediaFileInfo
# from vsutillib.misc import XLate


from mkvcommandparser import MKVCommandParser
from TrackOptions import TrackOptions
from verifystructure import VerifyStructure
from iso639 import iso639
from MergeOptions import MergeOptions
from MediaFileInfo import MediaFileInfo
from findSimilarTrack import findSimilarTrack


class TracksOrder:
    """
     TracksOrder
    """

    def __init__(self, trackOrder):

        self.__trackOrder = trackOrder
        self.__index = 0
        self.__aOrder = []
        self._split()

    def __getitem__(self, index):
        return self.__aOrder[index]

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index >= len(self.__aOrder):
            self.__index = 0
            raise StopIteration
        else:
            self.__index += 1
            return self.__getitem__(self.__index - 1)

    def _split(self):
        self.__aOrder = self.__trackOrder.split(",")

    @property
    def aOrder(self):
        return self.__aOrder

    @property
    def order(self):
        return self.__trackOrder


class IVerifyStructure(VerifyStructure):
    """
    IVerifyStructure VerifyStructure sub class do verification by index on
    MKVCommandParser object

    Args:
        oCommand (object): MKVCommandParser object
        index (int): index to verify
    """

    def __init__(self, oCommand=None, index=None):
        super().__init__()

        if oCommand is not None:
            if index is not None:
                self.verifyStructure(oCommand, index)

    def verifyStructure(self, oCommand, index):
        baseFiles = oCommand.baseFiles
        sourceFiles = oCommand.oSourceFiles[index]

        super().verifyStructure(baseFiles, sourceFiles)


def test():
    """
    test summary
    """
    cmd0 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'E:\Example\Series Title (2017)\Season 01\Episode - S01E03 (1).mkv' --language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:jpn --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng '(' 'E:\Example\Series Title (2017)\Season 01\Episode - S01E03.mkv' ')' --no-audio --no-video --sub-charset 2:UTF-8 --language 2:ita --track-name 2:Italian --default-track 2:yes '(' 'E:\Example\Series Title (2017)\New Sub\Episode (Italian Subs) - S01E03.mkv' ')' --title 'Episode 01' --track-order 0:0,0:1,1:2,0:2"
    cmd1 = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'E:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 10,11 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:ShowY --default-track 10:yes --sub-charset 11:UTF-8 --language 11:eng --track-name 11:Funimation '(' 'E:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:10,0:11"
    cmd = r"'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en --output 'E:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv' --audio-tracks 3 --subtitle-tracks 9,10 --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080 --language 3:jpn --default-track 3:yes --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation '(' 'E:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"
    option = r"--language 0:und --default-track 0:yes --display-dimensions 0:1280x720 --language 1:jpn --default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng"
    option2 = r"--no-audio --no-video --sub-charset 2:UTF-8 --language 2:ita --track-name 2:Italian --default-track 2:yes"

    """
    'C:/Program Files/MKVToolNix/mkvmerge.exe' --ui-language en
    --output 'E:\Example\TestMedia\Example 07\Arte (2020)\Season 01\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng) (1).mkv'
    --audio-tracks 3 --subtitle-tracks 9,10
    --language 0:und --default-track 0:yes --display-dimensions 0:1920x1080
    --language 3:jpn --default-track 3:yes
    --sub-charset 9:UTF-8 --language 9:eng --track-name 9:ShowY --default-track 9:yes
    --sub-charset 10:UTF-8 --language 10:eng --track-name 10:Funimation
    '(' 'E:\Example\TestMedia\Example 07\Source\Arte - 02 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv' ')' --track-order 0:0,0:3,0:9,0:10"

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

    # colorama.init()

    verify = IVerifyStructure()
    oCommand = MKVCommandParser()
    oCommand.command = cmd
    mOptions = MergeOptions()

    trackOptions = oCommand.oBaseFiles[0].trackOptions
    mediaInfo = oCommand.oBaseFiles[0].mediaFileInfo

    #print(trackOptions.tracks)

    for trk in trackOptions.tracks:
        print(trackOptions.optionsByTrack(trk))

    trackOptions.translation = {"9": "10", "10": "11"}
    print(trackOptions.strOptions())

    return

    for index, aF in enumerate(oCommand.oSourceFiles):
        verify.verifyStructure(oCommand, index)
        if not verify:
            print("Not Ok")
            for baseIndex, oBaseFile in enumerate(oCommand.oBaseFiles):

                baseFileInfo = oBaseFile.mediaFileInfo
                sourceFileInfo = MediaFileInfo(oCommand.oSourceFiles[index][baseIndex])

                translate = {}
                for track in oBaseFile.trackOptions.tracks:
                    i = int(track)
                    trackBase = baseFileInfo[i]
                    trackSource = sourceFileInfo[i]
                    if trackBase != trackSource:
                        print("Bad one.")
                        print(
                            f"  Track on Base: {trackBase.streamorder:2}: Type Order {trackBase.typeOrder} {trackBase.trackType} {trackBase.codec} {trackBase.language} {trackBase.title} ({trackBase.format})"
                        )
                        print(
                            f"Track on Source: {trackSource.streamorder:2}: Type Order {trackSource.typeOrder} {trackSource.trackType} {trackSource.codec} {trackSource.language} {trackSource.title} ({trackSource.format})"
                        )
                        trackSimilar, score = findSimilarTrack(
                            sourceFileInfo, trackBase
                        )

                        if trackSimilar >= 0:
                            translate[track] = str(trackSimilar)
                            trackSource = sourceFileInfo[trackSimilar]
                            print(
                                f"  Track Similar: {trackSource.streamorder:2}: Type Order {trackSource.typeOrder} {trackSource.trackType} {trackSource.codec} {trackSource.language} {trackSource.title} ({trackSource.format})\n"
                            )
                            print(f"track ID {trackSimilar} {score}")

                if translate:

                    print(f"For index {index} found translagion.")
                    trackOpts = copy.deepcopy(trackOptions)
                    print(trackOpts.strOptions())
                    trackOpts.translation = translate
                    print(trackOpts.strOptions())
                    return


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
    # xml = pymediainfo.MediaInfo.parse(r'E:\Example\TestMedia\Example 07\Source\Arte - 01 (BDRip 1920x1080 HEVC FLAC Rus + Jap + Eng).mkv', output="JSON")
    # f.write(xml.encode())
    # f.close()

    # for t in mediaInfo:
    #    print(t)

    # Separates optins exactly
    shellOptions = shlex.split(oCommand.oBaseFiles[0].options)

    trackOpts = []
    for index, option in enumerate(shellOptions):
        if mOptions.isTrackOption(option):
            parameter = (
                None if not mOptions.hasParameter(option) else shellOptions[index + 1]
            )
            trackOpts.append([option, index, parameter])

    currentTrack = ""

    reTrackID = re.compile(r"(\d+):(.*?)$")

    sTracks = []
    index = -1

    for opt in trackOpts:

        if mOptions.hasTrackID(opt[0]):
            if match := reTrackID.match(opt[2]):
                if currentTrack != match.group(1):
                    currentTrack = match.group(1)
                    index += 1
                    sTracks.append("")
                sTracks[index] += opt[0] + " " + opt[2]
        else:
            if currentTrack != "g":
                currentTrack = "g"
                index += 1
                sTracks.append("")
            if mOptions.hasParameter(opt[0]):
                sTracks[index] += opt[0] + " " + opt[2]
            else:
                sTracks[index] += opt[0] + " "

    # for trk in sTracks:
    #    print(f"{trk}")
    # Separate Options Exactly


if __name__ == "__main__":
    test()
