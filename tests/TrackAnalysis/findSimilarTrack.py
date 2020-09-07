"""Find Similar Track"""

def findSimilarTrack(sourceFile, track):
    """
    findSimilarTrack find a track similar to track in sourceFile

    Args:
        sourceFile (MediaInfoFile): MediaInfoFile object
        track (MediaTrack): MediaTrack object
    """

    basePoints = 0
    trackOrder = (-1)

    for trk in sourceFile:
        p = similarTrack(track, trk)
        if p > basePoints:
            basePoints = p
            trackOrder = trk.streamOrder

    return trackOrder, basePoints

def similarTrack(baseTrack, testTrack):
    """
    similarTrack find similarities and assign points

    Args:
        baseTrack (MediaTrack): base track
        testTrack (MediaTrack): track to test

    Returns:
        int: points awarded
    """

    points = 0

    if baseTrack.trackType != testTrack.trackType:
        return 0

    if baseTrack.language != testTrack.language:
        return 0

    if baseTrack.typeOrder == testTrack.typeOrder:
        points += 1

    if baseTrack.language == testTrack.language:
        points += 1

    if baseTrack.codec == testTrack.codec:
        points += 1

    if baseTrack.format == testTrack.format:
        points += 1

    if baseTrack.title == testTrack.title:
        points += 5

    return points
