"""Find Similar Track"""

def findSimilarTrack(oBaseFile, sourceFile, track, usedTracks, algorithm=1):
    """
    findSimilarTrack find a track similar to track in sourceFile

    Args:
        sourceFile (MediaInfoFile): MediaInfoFile object
        track (MediaTrack): MediaTrack object
    """

    basePoints = 0
    trackOrder = -1

    for trk in sourceFile:
        p = similarTrack(track, trk, oBaseFile, usedTracks, algorithm)
        if p > basePoints:
            basePoints = p
            trackOrder = trk.streamOrder

    return trackOrder, basePoints


def similarTrack(baseTrack, testTrack, baseFile, usedTracks, algorithm):
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

    # track already used
    if testTrack.streamOrder in usedTracks:
        return 0

    # is not the same type
    if baseTrack.trackType != testTrack.trackType:
        return 0

    points += 1

    # how many tracks of this type and language I need
    need = bTrkOpts.needTracksByTypeLanguage[baseTrack.trackType][
        baseTrack.language
    ]
    # is not the same language
    if baseTrack.language != testTrack.language:
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

    if algorithm == 1:
        # need more than available
        if need > testTrack.tracksLanguageOfThisKind:
            return 0

    points += 1

    # is same position by type
    if baseTrack.typeOrder == testTrack.typeOrder:
        points += 1

    # if in same position by type and language
    if baseTrack.typeLanguageOrder == testTrack.typeLanguageOrder:
        points += 1

    # is same codec (this is almost always none)
    if baseTrack.codec == testTrack.codec:
        points += 1

    # is same format
    if baseTrack.format == testTrack.format:
        points += 1

    # title is equal to source +5
    if baseTrack.title == testTrack.title:
        points += 5

    # special conditions for algorithm 2 None for now
    if algorithm == 2:
        pass

    return points
