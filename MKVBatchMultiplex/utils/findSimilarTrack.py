"""Find Similar Track"""

from .. import config


def findSimilarTrack(oBaseFile, sourceFile, track, usedTracks):
    """
    findSimilarTrack find a track similar to track in sourceFile

    Args:
        sourceFile (MediaInfoFile): MediaInfoFile object
        track (MediaTrack): MediaTrack object
    """

    basePoints = 0
    trackOrder = -1

    for trk in sourceFile:
        p = similarTrack(track, trk, oBaseFile, usedTracks)
        if p > basePoints:
            basePoints = p
            trackOrder = trk.streamOrder

    return trackOrder, basePoints


def similarTrack(baseTrack, testTrack, baseFile, usedTracks):
    """
    similarTrack find similarities and assign points

    Args:
        baseTrack (MediaTrack): base track
        testTrack (MediaTrack): track to test

    Returns:
        int: points awarded
    """

    bTrkOpts = baseFile.trackOptions

    points = 0

    if testTrack.streamOrder in usedTracks:
        return 0

    if baseTrack.trackType != testTrack.trackType:
        return 0

    points += 1

    if baseTrack.language != testTrack.language:
        if config.data.get(config.ConfigKey.Algorithm) >= 1:
            need = bTrkOpts.needTracksByTypeLanguage[baseTrack.trackType][
                baseTrack.language
            ]
            thisTypeTotal = bTrkOpts.needTracksByTypeLanguage[baseTrack.trackType][
                "all"
            ]
            if need == 1 and thisTypeTotal == 1:
                # Need one track have only one track and
                # one of the track language is undetermined
                if baseTrack.language is None or testTrack.language is None:
                    points += 1
                    return points
        return 0

    if config.data.get(config.ConfigKey.Algorithm) == 1:
        need = bTrkOpts.needTracksByTypeLanguage[baseTrack.trackType][
            baseTrack.language
        ]
        if need > testTrack.tracksLanguageOfThisKind:
            return 0

    points += 1

    if baseTrack.typeOrder == testTrack.typeOrder:
        points += 1
    else:
        # have to check
        # how many tracks of this type on base and source
        # one on base and one on source +1
        # one on base and more then one on source
        #     title is equal to source +5
        #     title differ +0
        # more than one on base one on source
        #     more selected than available +0
        #     title is equal to source +5
        pass

    if baseTrack.typeLanguageOrder == testTrack.typeLanguageOrder:
        points += 1

    if baseTrack.codec == testTrack.codec:
        points += 1

    if baseTrack.format == testTrack.format:
        points += 1

    if baseTrack.title == testTrack.title:
        points += 5

    if config.data.get(config.ConfigKey.Algorithm) == 2:
        pass

    return points
