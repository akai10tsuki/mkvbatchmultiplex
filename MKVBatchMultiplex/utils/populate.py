"""
 populate function for test development
"""

from ..jobs import JobStatus


def populate(model):

    data = testData()

    for r, d in enumerate(data):
        model.insertRows(r, 1, data=d)


def testData():
    """
    testData [summary]

    Args:
        dataRequest ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    data = [
        [
            [1, "", None],
            [JobStatus.AddToQueue, "Status code", None],
            [
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\New folder\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou"
                    r" ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn --track-name"
                    r" '0:10bit H.264 - 1080p' --default-track 0:yes --display-dimensions "
                    r"0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' --default-track 1:yes"
                    r" --sub-charset 2:UTF-8 --language 2:eng --track-name 2:FFF --default-track "
                    r"2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa "
                    r"Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' ')' "
                    r"--track-order 0:0,0:1,0:2"
                ),
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                None,
            ],
        ],
        [
            [2, "", None],
            [JobStatus.Waiting, "Status code", None],
            [
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                None,
            ],
        ],
        [
            [3, "", None],
            [JobStatus.AbortJobError, "", None],
            [
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                None,
            ],
        ],
        [
            [4, "", None],
            [JobStatus.Done, "Status code", None],
            [
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                None,
            ],
        ],
        [
            [5, "", None],
            [JobStatus.Aborted, "", None],
            [
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                (
                    r"'C:/Program Files/MKVToolNix\mkvmerge.exe' --ui-language en --output "
                    r"'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka"
                    r" [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo Motomeru no wa Machigatteiru "
                    r"Darou ka - 01 [BD][1080p-FLAC][8B5184BF] (1).mkv' --language 0:jpn "
                    r"--track-name '0:10bit H.264 - 1080p' --default-track 0:yes "
                    r"--display-dimensions 0:1920x1080 --language 1:jpn --track-name '1:2.0 FLAC' "
                    r"--default-track 1:yes --sub-charset 2:UTF-8 --language 2:eng --track-name "
                    r"2:FFF --default-track 2:yes '(' 'F:\BT\OK\[FFF] Dungeon ni Deai wo Motomeru "
                    r"no wa Machigatteiru Darou ka [BD][1080p-FLAC]\[FFF] Dungeon ni Deai wo "
                    r"Motomeru no wa Machigatteiru Darou ka - 01 [BD][1080p-FLAC][8B5184BF].mkv' "
                    r"')' --track-order 0:0,0:1,0:2"
                ),
                None,
            ],
        ],
    ]

    return data
