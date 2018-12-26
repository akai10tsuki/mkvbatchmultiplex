#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get information from media file structure

MC018
"""

import logging

from pymediainfo import MediaInfo

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())

class MediaFileInfo(object):
    """
    Media file properties
    This class main function is to verify that the structure of the files
    is the same:

        Same order of tracks
        Same language if it applies

    :param strMediaFile: name with fullpath of source file
    :type strMediaFile: str
    :param log: activate log
    :type log: bool
    """

    def __init__(self, strMediaFile, log=False):

        self.fileName = strMediaFile
        self.codec = ""
        self.format = ""
        self.lstMediaTracks = []
        self.log = log

        self._initHelper()

    def _initHelper(self):

        try:
            fileMediaInfo = MediaInfo.parse(self.fileName)
        except OSError:
            raise OSError("MediaInfo not found.")

        for track in fileMediaInfo.tracks:
            if track.track_type == "General":
                self.codec = track.codec
                self.format = track.format
            if track.track_type in ("Video", "Audio", "Text"):
                self.lstMediaTracks.append(
                    _MediaTrackInfo(
                        track.streamorder,
                        track.track_type,
                        track.language,
                        track.default,
                        track.forced,
                        track.title,
                        track.codec,
                        track.format
                    )
                )

    def __len__(self):
        return len(self.lstMediaTracks) if self.lstMediaTracks else 0

    def __eq__(self, objOther):

        bReturn = True

        if self.log:
            MODULELOG.debug(
                "MC006: Structure equality test between [%s] and [%s]",
                self.fileName,
                objOther.fileName
            )
            MODULELOG.debug("MC007: FORMAT: %s", self.format)

        if self.codec != objOther.codec:
            if self.log:
                MODULELOG.debug(
                    "MC008: Codec mismatched %s - %s",
                    self.codec, objOther.codec
                )
            bReturn = False
        elif len(self) != len(objOther):
            if self.log:
                MODULELOG.debug(
                    "MC009: Number of tracks mismatched %s - %s",
                    len(self), len(objOther)
                )
            bReturn = False
        elif len(self) == len(objOther):
            for a, b in zip(self.lstMediaTracks, objOther.lstMediaTracks):
                if a.streamorder != b.streamorder:
                    if self.log:
                        MODULELOG.debug(
                            "MC010:  Stream order mismatched %s - %s",
                            a.streamorder, b.streamorder
                        )
                    bReturn = False
                elif a.track_type != b.track_type:
                    if self.log:
                        MODULELOG.debug(
                            "MC011: Stream type mismatched %s - %s",
                            a.track_type, b.track_type
                        )
                    bReturn = False
                elif a.language != b.language:
                    if self.log:
                        MODULELOG.debug(
                            "MC012: Stream language mismatched %s - %s",
                            a.language, b.language
                        )
                    if self.format != 'AVI':
                        # Ignore language for AVI container
                        if self.log:
                            MODULELOG.debug(
                                "MC013: AVI container ignore language mismatched %s - %s",
                                a.track_type, b.track_type
                            )
                    else:
                        bReturn = False
                elif (a.codec != b.codec) and (a.track_type != "Audio"):
                    if self.log:
                        MODULELOG.debug(
                            "MC014: Codec mismatched %s - %s",
                            a.codec, b.codec
                        )
                    if self.format == 'AVI':
                        # Ignore language for AVI container
                        if self.log:
                            MODULELOG.debug(
                                "MC015: AVI container ignore codec mismatched %s - %s",
                                a.codec, b.codec
                            )
                    else:
                        bReturn = False
                elif a.format != b.format:
                    if self.log:
                        MODULELOG.debug(
                            "MC016: Stream format mismatched %s - %s",
                            a.format, b.format
                        )
                    bReturn = False

        if self.log and bReturn:
            MODULELOG.debug(
                "MC017: Structure found ok.",
            )

        return bReturn

    def __str__(self):

        tmpStr = "File Nme: {}\nFile Format: -{}-\n\n".format(
            self.fileName, self.format)
        tmpNum = 1

        for track in self.lstMediaTracks:
            tmpStr += "Track: {}\n".format(tmpNum)
            tmpStr += "Order: {} - {}\n".format(
                track.streamorder, track.track_type)
            tmpStr += "Codec: {}\n".format(track.codec)
            tmpStr += "Language: {}\n".format(track.language)
            tmpStr += "Format: {}\n".format(track.format)
            tmpNum += 1

        return tmpStr


class _MediaTrackInfo(object):
    """Media track properties"""

    def __init__(self, streamorder=None, track_type=None,
                 language=None, default=None,
                 forced=None, title=None,
                 codec=None, format_=None):

        self.streamorder = streamorder
        self.track_type = track_type  # pylint: disable=C0103
        self.language = language
        self.default = default
        self.forced = forced
        self.title = title
        self.codec = codec
        self.format = format_

    def __str__(self):
        return "Stream Order: " + self.streamorder \
            + "\nTrack Type: " + self.track_type \
            + "\nLanguage: " + self.language \
            + "\nDefault Track : " + self.default \
            + "\nForced Track: " + self.forced \
            + "\nTrack Title: " + self.title \
            + "\nCodec: " + self.codec \
            + "\nFormat: " + self.format \
            + "\n"
