"""
CommandWidget helper functions attach to buttons
"""

# pylint: disable=bad-continuation

from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QLineEdit

import vsutillib.mkv as mkv
from vsutillib.pyqt import SvgColor, LineOutput, checkColor

from .. import config

def runAnalysis(**kwargs):
    """List the source files found"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    log = kwargs.pop("log", False)
    if command:
        output.command.emit("Analysis of command line:\n", {LineOutput.AppendEnd: True})
        verify = mkv.MKVCommandParser(command, log=log)
        verify.generateCommands()
        for e in verify.analysis:
            if e.find(r"chk:") >= 0:
                output.command.emit(
                    "{}".format(e),
                    {LineOutput.Color: SvgColor.green, LineOutput.AppendEnd: True},
                )
            else:
                output.command.emit(
                    "{}".format(e),
                    {LineOutput.Color: SvgColor.red, LineOutput.AppendEnd: True},
                )
        output.command.emit("\n", {LineOutput.AppendEnd: True})


def runAnalysisOld(**kwargs):
    """List the source files found"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    log = kwargs.pop("log", False)
    verify = mkv.VerifyMKVCommand(command, log=log)
    output.command.emit("Analysis of command line:\n", {LineOutput.AppendEnd: True})

    for e in verify.analysis:
        if e.find(r"chk:") >= 0:
            output.command.emit(
                "{}".format(e),
                {LineOutput.Color: SvgColor.darkgreen, LineOutput.AppendEnd: True},
            )
        else:
            output.command.emit(
                "{}".format(e),
                {LineOutput.Color: SvgColor.red, LineOutput.AppendEnd: True},
            )

    output.command.emit("\n", {LineOutput.AppendEnd: True})


def showCommands(**kwargs):
    """List the commands to be executed"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)
    log = kwargs.pop("log", False)
    index = 1

    if oCommand is None:
        oCommand = mkv.MKVCommandParser(command, log=log)

    if output is None:
        return "No output callback function"

    output.command.emit(
        "Shell:\n\n{}\n".format(oCommand.command), {LineOutput.AppendEnd: True}
    )

    if not oCommand.commandsGenerated:
        output.command.emit("Generating Commands...\n", {LineOutput.AppendEnd: True})
        oCommand.generateCommands()

    output.command.emit(
        "Command Template:\n\n{}\n\nCommands:\n".format(str(oCommand.commandTemplate)),
        {LineOutput.AppendEnd: True},
    )

    if oCommand:
        for command, _, _, _, _, _, _ in oCommand:
            output.command.emit(
                "Command {}.\n{}".format(index, str(command)) + "\n",
                {LineOutput.AppendEnd: True},
            )
            index += 1
    else:
        output.command.emit(
            "MCW0008: Error in command construction {}\n".format(oCommand.error),
            {LineOutput.Color: Qt.red, LineOutput.AppendEnd: True},
        )

    output.command.emit("", {LineOutput.AppendEnd: True})

    return None


def checkFiles(**kwargs):
    """Check file structure against primary source file"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)
    log = kwargs.pop("log", False)

    if oCommand is None:
        oCommand = mkv.MKVCommandParser(command, log=log)

    if output is None:
        return "No output callback function"

    output.command.emit("Checking files...\n", {LineOutput.AppendEnd: True})

    if not oCommand.commandsGenerated:
        output.command.emit("Generating Commands...\n", {LineOutput.AppendEnd: True})
        oCommand.generateCommands()

    if oCommand:
        verify = mkv.VerifyStructure(log=log)

        for index, (_, baseFiles, sourceFiles, destinationFile, _, _, _) in enumerate(
            oCommand
        ):
            verify.verifyStructure(baseFiles, sourceFiles)
            lstFile = []

            for f in sourceFiles:
                lstFile.append(str(f))

            if verify:
                msg = "{}. Source: {}\nDestination: {}\nStructure looks Ok.\n"
                msg = msg.format(index + 1, str(lstFile), destinationFile)
                output.command.emit(
                    msg, {LineOutput.Color: Qt.darkGreen, LineOutput.AppendEnd: True}
                )
            else:
                msg = "{}. Source: {}\nDestination: {}\nStructure Error.\n"
                msg = msg.format(index + 1, str(lstFile), destinationFile)
                output.command.emit(
                    msg,
                    {
                        LineOutput.Color: SvgColor.yellowgreen,
                        LineOutput.AppendEnd: True,
                    },
                )

                for i, m in enumerate(verify.analysis):
                    if i == 0:
                        output.command.emit(
                            m.strip() + "\n",
                            {
                                LineOutput.Color: SvgColor.orange,
                                LineOutput.AppendEnd: True,
                            },
                        )
                    else:
                        output.command.emit(
                            str(i) + ". " + m.strip(),
                            {
                                LineOutput.Color: SvgColor.red,
                                LineOutput.AppendEnd: True,
                            },
                        )

                output.command.emit("", {LineOutput.AppendEnd: True})

        output.command.emit("", {LineOutput.AppendEnd: True})

    return None


class QLineEditWidget(QLineEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            print("Ctrl-V Paste Filter")

        super().keyPressEvent(event)

    def contextMenuEvent(self, event):

        print(str(event))

        print(self.text())

        super().contextMenuEvent(event)
