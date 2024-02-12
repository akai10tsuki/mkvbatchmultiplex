"""
CommandWidget helper functions attach to buttons
"""

import logging

from threading import Lock

from PySide6.QtCore import Qt

import vsutillib.mkv as mkv
from vsutillib.files import DisplayPath
from vsutillib.pyside6 import LineOutput, SvgColor

from .. import config


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def runAnalysis(**kwargs: str) -> None:
    """List the source files found"""

    output = kwargs.pop(MKVParseKey.output, None)
    command = kwargs.pop(MKVParseKey.command, None)
    oCommand= kwargs.pop(MKVParseKey.oCommand, None)
    appDir = kwargs.pop(MKVParseKey.appDir, None)
    log = kwargs.pop(MKVParseKey.log, False)

    if output is None:
        if log:
            MODULELOG.error(
                "[runAnalysis] "
                "No output callback function")
        return "No output callback function"

    if (command is not None) and (appDir is not None):
        output.command.emit("Analysis of command line:\n",
                            {LineOutput.AppendEnd: True})

        useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)
        # Creating a new MKVCommandParser object
        # TODO: check if using CommandWidget is ok
        if oCommand is None:
            verify = mkv.MKVCommandParser(
                command,
                appDir=appDir,
                useEmbedded=useEmbedded,
                log=log)
            verify.generateCommands()
            print("runAnalysis new oCommand")
        else:
            verify = oCommand
            print("runAnalysis old oCommand")

        if verify.analysis:
            for e in verify.analysis:
                if e.find(r"chk:") >= 0:
                    output.command.emit(
                        f"{e}",
                        {LineOutput.Color: SvgColor.green,
                        LineOutput.AppendEnd: True},
                    )
                else:
                    output.command.emit(
                        f"{e}",
                        {LineOutput.Color: SvgColor.red,
                        LineOutput.AppendEnd: True},
                    )
            output.command.emit("\n", {LineOutput.AppendEnd: True})
        else:
            output.command.emit(
                "No analysis to display.\n", {LineOutput.AppendEnd: True})
            if log:
                MODULELOG.warning(
                    "[runAnalysis] "
                    "No analysis to display.")
    else:
        if log:
            MODULELOG.error(
                "[runAnalysis] "
                "wrong parameters.")


def showCommands(**kwargs: str):
    """List the commands to be executed"""

    output = kwargs.pop(MKVParseKey.output, None)
    command = kwargs.pop(MKVParseKey.command, None)
    oCommand = kwargs.pop(MKVParseKey.oCommand, None)
    appDir = kwargs.pop(MKVParseKey.appDir, None)
    log = kwargs.pop(MKVParseKey.log, False)
    index = 1

    if output is None:
        if log:
            MODULELOG.error(
                f"[CommandWidgetHelpers.showCommands] "
                f"No output callback function")
        return "No output callback function"

    output.command.emit(
        f"Show Commands Working...\n",
        {LineOutput.AppendEnd: True}
    )

    useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)

    if (oCommand is None):
        oCommand = mkv.MKVCommandParser(
            command,
            appDir=appDir,
            useEmbedded=useEmbedded,
            log=log)
        print("new oCommand")
    else:
        oCommand.command = command
        oCommand.useEmbedded = useEmbedded
        print("old oCommand")

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

    output = kwargs.pop(MKVParseKey.output, None)
    command = kwargs.pop(MKVParseKey.command, None)
    oCommand= kwargs.pop(MKVParseKey.oCommand, None)
    appDir = kwargs.pop(MKVParseKey.appDir, None)
    log = kwargs.pop(MKVParseKey.log, False)

    if output is None:
        if log:
            MODULELOG.error(
                f"[CommandWidgetHelpers.chkFiles] "
                f"No output callback function")
        return "No output callback function"

    lock = Lock()

    if oCommand is None:
        useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)
        verify = mkv.MKVCommandParser(
            command,
            appDir=appDir,
            useEmbedded=useEmbedded,
            log=log)
        verify.generateCommands()
        print("checkFiles new oCommand")
    else:
        verify = oCommand
        print("checkFiles old oCommand")

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

                with lock:
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

    output = kwargs.pop(MKVParseKey.output, None)
    command = kwargs.pop(MKVParseKey.command, None)
    oCommand= kwargs.pop(MKVParseKey.oCommand, None)
    appDir = kwargs.pop(MKVParseKey.appDir, None)
    log = kwargs.pop(MKVParseKey.log, False)

    if output is None:
        if log:
            MODULELOG.error(
                f"[CommandWidgetHelpers.showCommands] "
                f"No output callback function")
        return "No output callback function"

    output.command.emit(
        f"Show Commands Working...\n",
        {LineOutput.AppendEnd: True}
    )

    useEmbedded = config.data.get(config.ConfigKey.UseEmbedded)

    if (oCommand is None):
        oCommand = mkv.MKVCommandParser(
            command,
            appDir=appDir,
            useEmbedded=useEmbedded,
            log=log)
        print("sourceTree new oCommand")
    else:
        #oCommand.useEmbedded = useEmbedded
        #oCommand.command = command
        print("sourceTree old oCommand")

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
    output = "output"
    command = "command"
    oCommand = "oCommand"
    appDir = "appDir"
    log = "log"
