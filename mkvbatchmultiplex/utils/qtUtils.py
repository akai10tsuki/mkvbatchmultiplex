"""
qtUtils:

utility functions that use PySide2
"""

import logging
import re
import subprocess


from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDesktopWidget


from ..jobs import JobStatus


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


def centerWidgets(widget, parent=None):
    """center widget based on parent or screen geometry"""

    if parent:
        widget.move(parent.frameGeometry().center() - widget.frameGeometry().center())

        #hostRect = parent.geometry()
        #widget.frameGeometry().moveCenter(hostRect.center())
        #widget.move(hostRect.center() - widget.rect().center())

        #parentCenter = parent.frameGeometry().center()
        #widgetFrameGeometry = widget.frameGeometry()
        #widgetFrameGeometry.moveCenter(parentCenter)
        #widget.move(widgetFrameGeometry.topLeft())


    else:
        print("Second option...")
        widget.move(QDesktopWidget().availableGeometry().center() - widget.frameGeometry().center())


def runCommand(command, currentJob, lstTotal, log=False):
    """Execute command in a subprocess thread"""

    regEx = re.compile(r"(\d+)")

    iTotal = 0
    rc = 1000

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as p:
        addNewline = True
        iTotal = lstTotal[0]
        n = 0

        for line in p.stdout:

            rcResult = p.poll()
            if rcResult is not None:
                rc = rcResult

            if line.find(u"Progress:") == 0:
                # Deal with progress percent
                if addNewline:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        "",
                        {'appendLine': True}
                    )
                    addNewline = False

                m = regEx.search(line)

                if m:
                    n = int(m.group(1))

                if n > 0:
                    currentJob.outputJobMain(
                        currentJob.jobID,
                        line.strip(),
                        {'replaceLine': True}
                    )
                    currentJob.progressBar.emit(n, iTotal + n)

            else:

                #if  not line.strip("\n"):
                #    currentJob.outputJobMain(currentJob.jobID, "\n\n", {})
                #else:
                if line.find(u"Warning") == 0:
                    currentJob.outputJobMain(
                        currentJob.jobID, line,
                        {'color': Qt.red, 'appendLine': True},
                        True
                    )
                elif line.find(u"Error") == 0:
                    currentJob.outputJobMain(
                        currentJob.jobID, line,
                        {'color': Qt.red, 'appendLine': True},
                        True
                    )
                    lstTotal[2] += 1
                    if line.find("There is not enough space") >= 0:
                        currentJob.controlQueue.put(JobStatus.AbortJobError)
                else:
                    currentJob.outputJobMain(
                        currentJob.jobID, line.strip(), {'appendLine': True}
                    )

            if not currentJob.spControlQueue.empty():
                request = currentJob.spControlQueue.get()
                if request == JobStatus.AbortJob:
                    currentJob.controlQueue.put(JobStatus.AbortJob)
                    p.kill()
                    outs, errs = p.communicate()
                if request == JobStatus.Abort:
                    currentJob.controlQueue.put(JobStatus.AbortForced)
                    p.kill()
                    outs, errs = p.communicate()
                    if outs:
                        print(outs)
                    if errs:
                        print(errs)
                    print(p.returncode)
                    break

        currentJob.outputJobMain(
            currentJob.jobID,
            "\n",
            {'appendLine': True}
        )

    lstTotal[0] += 100

    if log:
        MODULELOG.info("UTL0001: runCommand rc=%d - %s", rc, command)

    return rc
