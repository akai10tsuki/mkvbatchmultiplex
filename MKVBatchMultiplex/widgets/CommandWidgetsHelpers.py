"""
CommandWidget helper functions attach to buttons
"""

from PySide2.QtCore import Qt

import vsutillib.mkv as mkv

def runAnalysis(**kwargs):
    """List the source files found"""

    output = kwargs.pop('output', None)
    command = kwargs.pop('command', None)

    verify = mkv.VerifyMKVCommand(command)

    output.command.emit("Analysis of command line:\n\n", {})

    for e in verify.analysis:
        if e.find(r"chk:") >= 0:
            output.command.emit("{}\n".format(e), {"color": Qt.darkGreen})
        else:
            output.command.emit("{}\n".format(e), {"color": Qt.red})

    output.command.emit("\n", {})

def showCommands(**kwargs):
    """List the commands to be executed"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop('oCommand', None)

    if oCommand is None:
        oCommand = mkv.MKVCommand(command)

    if output is None:
        return "No output callback function"

    output.command.emit("Shell:\n\n{}\n\n".format(oCommand.command), {})
    output.command.emit(
        "Command Template:\n\n{}\n\nCommands:\n\n".format(str(oCommand.template)),
        {},
    )

    if oCommand:
        for command, _, _, _, _ in oCommand:
            output.command.emit(str(command) + "\n\n", {})
    else:
        output.command.emit(
            "MCW0008: Error in command construction {}\n\n".format(oCommand.error),
            {"color": Qt.red},
        )

    output.command.emit("\n", {})

    return None

def checkFiles(**kwargs):
    """Check file structure against primary source file"""

    output = kwargs.pop("output", None)
    command = kwargs.pop("command", None)
    oCommand = kwargs.pop('oCommand', None)

    if oCommand is None:
        oCommand = mkv.MKVCommand(command)

    if output is None:
        return "No output callback function"

    output.command.emit("Checking files...\n\n", {})

    if oCommand:

        verify = mkv.VerifyStructure()

        for _, basefiles, sourcefiles, _, _ in oCommand:

            verify.verifyStructure(basefiles, sourcefiles)

            if verify:
                lstFile = []
                for f in sourcefiles:
                    lstFile.append(str(f))

                output.command.emit(
                    "Structure looks OK:\n"
                    + str(lstFile) + "\n\n",
                    {'color': Qt.darkGreen}
                )
            else:
                output.command.emit(
                    str(verify)
                    + "\n\n",
                    {'color': Qt.red}
                )

    output.command.emit("\n", {})

    return None
