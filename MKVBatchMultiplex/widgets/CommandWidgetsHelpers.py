"""
CommandWidget helper functions attach to buttons
"""

from PySide6.QtCore import Qt

import vsutillib.mkv as mkv
from vsutillib.files import DisplayPath
from vsutillib.pyside6 import LineOutput, SvgColor


def runAnalysis(**kwargs: str) -> None:
    """List the source files found"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    log = kwargs.pop("log", False)

    if command:
        output.command.emit("Analysis of command line:\n",
                            {LineOutput.AppendEnd: True})
        verify = mkv.MKVCommandParser(command, log=log)
        verify.generateCommands()
        for e in verify.analysis:
            if e.find(r"chk:") >= 0:
                output.command.emit(
                    f"{e}",
                    {LineOutput.Color: SvgColor.green, LineOutput.AppendEnd: True},
                )
            else:
                output.command.emit(
                    f"{e}",
                    {LineOutput.Color: SvgColor.red, LineOutput.AppendEnd: True},
                )
        output.command.emit("\n", {LineOutput.AppendEnd: True})


def runAnalysisOld(**kwargs):
    """List the source files found"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    log = kwargs.pop("log", False)
    verify = mkv.VerifyMKVCommand(command, log=log)
    output.command.emit("Analysis of command line:\n",
                        {LineOutput.AppendEnd: True})

    for e in verify.analysis:
        if e.find(r"chk:") >= 0:
            output.command.emit(
                f"{e}",
                {LineOutput.Color: SvgColor.darkgreen, LineOutput.AppendEnd: True},
            )
        else:
            output.command.emit(
                f"{e}",
                {LineOutput.Color: SvgColor.red, LineOutput.AppendEnd: True},
            )

    output.command.emit("\n", {LineOutput.AppendEnd: True})


def showCommands(**kwargs: str):
    """List the commands to be executed"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)
    log = kwargs.pop("log", False)
    index = 1

    oCommand = mkv.MKVCommandParser(command, log=log)

    if output is None:
        return "No output callback function"

    output.command.emit(
        f"Shell:\n\n{oCommand.command}\n", {LineOutput.AppendEnd: True}
    )

    if not oCommand.commandsGenerated:
        output.command.emit("Generating Commands...\n", {
                            LineOutput.AppendEnd: True})
        oCommand.generateCommands()

    output.command.emit(
        f"Command Template:\n\n{str(oCommand.commandTemplate)}\n\nCommands:\n",
        {LineOutput.AppendEnd: True},
    )

    if oCommand:
        for command, _, _, _, _, _, _ in oCommand:
            output.command.emit(
                f"Command {index}.\n{str(command)}\n",
                {LineOutput.AppendEnd: True},
            )
            index += 1
    else:
        output.command.emit(
            "MCW0008: Error in command construction.\n",
            {LineOutput.Color: Qt.red, LineOutput.AppendEnd: True},
        )

    output.command.emit("", {LineOutput.AppendEnd: True})

    return None


def checkFiles(**kwargs: str) -> str:
    """Check file structure against primary source file"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)
    log = kwargs.pop("log", False)

    oCommand = mkv.MKVCommandParser(command, log=log)

    dictStats = {}
    errorFound = False
    errorMarker = False

    if output is None:
        return "No output callback function"

    output.command.emit("Checking files...\n", {LineOutput.AppendEnd: True})

    if not oCommand.commandsGenerated:
        output.command.emit("Generating Commands...\n", {
                            LineOutput.AppendEnd: True})
        oCommand.generateCommands()

    if oCommand:

        verify = mkv.VerifyStructure(log=log)

        for n, (_, baseFiles, sourceFiles, destinationFile, _, _, _) in enumerate(
            oCommand
        ):
            verify.verifyStructure(baseFiles, sourceFiles)
            lstFile = []
            index = n + 1
            for f in sourceFiles:
                lstFile.append(str(f))

            msg = (f"{index}. Source: {str(lstFile)}\nDestination: "
                   f"{destinationFile}\n")

            if verify:
                msg += "Structure looks Ok.\n"
                dictStats[index] = (True, msg, {LineOutput.Color: Qt.darkGreen,
                                                LineOutput.AppendEnd: True})

            else:
                errorFound = True
                msg += "Structure Error.\n"
                dictStats[index] = (
                    False,
                    msg,
                    {LineOutput.Color: SvgColor.yellowgreen,
                     LineOutput.AppendEnd: True})

                for i, m in enumerate(verify.analysis):
                    if i == 0:
                        output.error.emit(
                            m.strip() + "\n",
                            {
                                LineOutput.Color: SvgColor.orange,
                                LineOutput.AppendEnd: True,
                            },
                        )
                    else:
                        output.error.emit(
                            str(i) + " - " + m.strip(),
                            {
                                LineOutput.Color: SvgColor.red,
                                LineOutput.AppendEnd: True,
                            },
                        )

                output.error.emit("", {LineOutput.AppendEnd: True})

        startIndex = None
        endIndex = None
        status = None
        bPrint = False
        dictLen = len(dictStats)

        for i, (valid, message, dictMessage) in dictStats.items():

            if status is None:
                status = valid
                startIndex = i
            else:
                if status != valid:
                    bPrint = True
                    endIndex = (i - 1)  # if (i > 1) else None

            if bPrint or (i == dictLen):
                if endIndex is not None:
                    (msg, dictMsg) = validMessage(status)
                    output.command.emit(
                        f"Commands from: {startIndex}-{endIndex} "
                        f"- {msg}\n",
                        dictMsg
                    )
                else:
                    (msg, dictMsg) = validMessage(status)
                    output.command.emit(
                        f"Command: {startIndex} "
                        f"- {msg}\n",
                        dictMsg
                    )
                if (i == dictLen) and (i != endIndex):
                    (msg, dictMsg) = validMessage(valid)
                    output.command.emit(
                        f"Command: {i} - {msg}\n",
                        dictMsg
                    )

                bPrint = False
                status = valid
                startIndex = i
                endIndex = None

        output.command.emit("", {LineOutput.AppendEnd: True})

    else:

        output.command.emit("Cannot generate commands.\n",
                            {LineOutput.AppendEnd: True})


def sourceTree(**kwargs: str) -> None:
    """Check file structure against primary source file"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)
    log = kwargs.pop("log", False)

    oCommand = mkv.MKVCommandParser(command, log=log)

    if not oCommand.commandsGenerated:
        output.command.emit("Generating Commands...\n", {
                            LineOutput.AppendEnd: True})
        oCommand.generateCommands()

    baseTotalFiles = 0
    for key in oCommand.filesInDirByKey.keys():

        if key == MKVParseKey.title:
            continue

        if baseTotalFiles == 0:
            baseTotalFiles = len(tuple(oCommand.filesInDirByKey[key]))
        totalFiles = len(tuple(oCommand.filesInDirByKey[key]))

        color = SvgColor.green

        if baseTotalFiles != totalFiles:
            color = SvgColor.red

        output.command.emit(
            f"Files for key - {key} total is {totalFiles}",
            {LineOutput.Color: color, LineOutput.AppendEnd: True},
        )

        if baseTotalFiles != totalFiles:
            color = SvgColor.orange

        if key in oCommand.dirsByKey.keys():
            output.command.emit(
                f"Directory: {oCommand.dirsByKey[key]}\n",
                {LineOutput.Color: color, LineOutput.AppendEnd: True},
            )
            dirTree = DisplayPath.makeTree(
                oCommand.dirsByKey[key], fileList=oCommand.filesInDirByKey[key]
            )
            for child in dirTree:
                output.command.emit(
                    f"{child.displayable()}",
                    {LineOutput.Color: color, LineOutput.AppendEnd: True},
                )

            output.command.emit(
                "",
                {LineOutput.Color: color, LineOutput.AppendEnd: True},
            )

    output.command.emit(
        f"Files in destination directory: {oCommand.dirsByKey[MKVParseKey.outputFile]}\n",
        {LineOutput.Color: color, LineOutput.AppendEnd: True},
    )
    dirTree = DisplayPath.makeTree(oCommand.dirsByKey[MKVParseKey.outputFile])
    for child in dirTree:
        output.command.emit(
            f"{child.displayable()}",
            {LineOutput.Color: color, LineOutput.AppendEnd: True},
        )

    output.command.emit(
        "",
        {LineOutput.Color: color, LineOutput.AppendEnd: True},
    )


def validMessage(ok: bool) -> tuple:
    if ok:
        return ("Structure looks Ok.", {LineOutput.Color: Qt.darkGreen,
                                        LineOutput.AppendEnd: True})
    return ("Structure Error.", {LineOutput.Color: SvgColor.yellowgreen,
                                 LineOutput.AppendEnd: True})


class MKVParseKey:

    attachmentFiles = "<ATTACHMENTS>"
    chaptersFile = "<CHAPTERS>"
    outputFile = "<OUTPUTFILE>"
    title = "<TITLE>"
