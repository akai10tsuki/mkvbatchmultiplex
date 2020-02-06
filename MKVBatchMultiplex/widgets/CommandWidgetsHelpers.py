"""
CommandWidget helper functions attach to buttons
"""

# pylint: disable=bad-continuation

from PySide2.QtCore import Qt

import vsutillib.mkv as mkv
from vsutillib.pyqt import SvgColor


def runAnalysis(**kwargs):
    """List the source files found"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)

    verify = mkv.VerifyMKVCommand(command)

    output.command.emit("Analysis of command line:\n", {"appendEnd": True})

    for e in verify.analysis:
        if e.find(r"chk:") >= 0:
            output.command.emit(
                "{}".format(e), {"color": SvgColor.darkgreen, "appendEnd": True}
            )
        else:
            output.command.emit(
                "{}".format(e), {"color": SvgColor.red, "appendEnd": True}
            )

    output.command.emit("\n", {"appendEnd": True})


def showCommands(**kwargs):
    """List the commands to be executed"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)

    if oCommand is None:
        oCommand = mkv.MKVCommand(command)

    if output is None:
        return "No output callback function"

    output.command.emit("Shell:\n\n{}\n".format(oCommand.command), {"appendEnd": True})
    output.command.emit(
        "Command Template:\n\n{}\n\nCommands:\n".format(str(oCommand.template)),
        {"appendEnd": True},
    )

    if oCommand:
        for command, _, _, _, _ in oCommand:
            output.command.emit(str(command) + "\n", {"appendEnd": True})
    else:
        output.command.emit(
            "MCW0008: Error in command construction {}\n".format(oCommand.error),
            {"color": Qt.red, "appendEnd": True},
        )

    output.command.emit("", {"appendEnd": True})

    return None


def checkFiles(**kwargs):
    """Check file structure against primary source file"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop("oCommand", None)

    if oCommand is None:
        oCommand = mkv.MKVCommand(command)

    if output is None:
        return "No output callback function"

    output.command.emit("Checking files...\n", {"appendEnd": True})

    if oCommand:

        verify = mkv.VerifyStructure()

        for index, (_, baseFiles, sourceFiles, destinationFile, _) in enumerate(
            oCommand
        ):

            verify.verifyStructure(baseFiles, sourceFiles)

            lstFile = []
            for f in sourceFiles:
                lstFile.append(str(f))

            if verify:

                msg = "{}. Source: {}\nDestination: {}\nStructure looks Ok.\n"
                msg = msg.format(index + 1, str(lstFile), destinationFile)

                output.command.emit(msg, {"color": Qt.darkGreen, "appendEnd": True})

            else:

                msg = "{}. Source: {}\nDestination: {}\nStructure Error.\n"
                msg = msg.format(index + 1, str(lstFile), destinationFile)

                output.command.emit(
                    msg, {"color": SvgColor.yellowgreen, "appendEnd": True}
                )

                for i, m in enumerate(verify.analysis):
                    if i == 0:
                        output.command.emit(
                            m.strip() + "\n",
                            {"color": SvgColor.orange, "appendEnd": True},
                        )
                    else:
                        output.command.emit(
                            str(i) + ". " + m.strip(),
                            {"color": SvgColor.red, "appendEnd": True},
                        )

    output.command.emit("", {"appendEnd": True})

    return None
