"""
jobsWorker
"""

import logging

# try:
#    import cPickle as pickle
# except ImportError:  # pylint: disable=bare-except
#    import pickle
import re

# import sys
# import zlib
# import pprint

from datetime import datetime
from time import time, sleep

from PySide2.QtWidgets import QSystemTrayIcon

import vsutillib.mkv as mkv

from vsutillib.misc import staticVars, strFormatTimeDelta
from vsutillib.process import RunCommand
from vsutillib.pyqt import SvgColor

from .. import config

# from ..utils import adjustSources

from .jobsDB import saveToDb
from .JobKeys import JobStatus, JobKey
from .SqlJobsTable import SqlJobsTable


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


@staticVars(running=False)
def jobsWorker(
    jobsQueue,
    output,
    proxyModel,
    funcProgress,
    controlQueue,
    trayIconMessageSignal,
    log=False,
):
    """
    jobsWorker execute jobs on queue

    Args:
        jobsQueue (jobsQueue): Job queue has all related information for the job
        funcProgress (func): function to call to report job progress. Defaults to None.

    Returns:
        str: Dummy  return value
    """

    #
    # Always open to start saving in mid of worker operating
    #
    jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))

    if jobsWorker.running:
        # Block direct calls while working there should be none
        return "Working..."

    jobsWorker.running = True
    totalJobs = len(jobsQueue)
    remainingJobs = totalJobs - 1
    currentJob = 0
    indexTotal = [0, 0]
    verify = mkv.VerifyStructure(log=log)
    iVerify = mkv.IVerifyStructure()
    totalErrors = funcProgress.lbl[4]
    abortAll = False
    bSimulateRun = config.data.get(config.ConfigKey.SimulateRun)
    model = proxyModel.sourceModel()

    while job := jobsQueue.popLeft():

        # job = copy.deepcopy(qJob)

        job.jobRow = model.dataset[
            job.jobRowNumber,
        ]
        statusIndex = model.index(job.jobRowNumber, JobKey.Status)

        if abortAll:
            jobsQueue.statusUpdateSignal.emit(job, JobStatus.Aborted)
            continue

        actualRemaining = len(jobsQueue)

        if actualRemaining == remainingJobs:
            remainingJobs -= 1
        else:
            totalJobs = totalJobs + actualRemaining - remainingJobs
            remainingJobs = actualRemaining - 1

        currentJob += 1
        indexTotal[0] = 0  # file index
        indexTotal[1] = 0  # current max progress bar
        totalFiles = 0

        if job.oCommand:
            totalFiles = len(job.oCommand)

        maxBar = totalFiles * 100
        funcProgress.pbSetValues.emit(0, 0)
        funcProgress.pbSetMaximum.emit(100, maxBar)
        funcProgress.lblSetValue.emit(0, totalJobs)
        funcProgress.lblSetValue.emit(1, currentJob)
        funcProgress.lblSetValue.emit(3, totalFiles)
        indexTotal[0] = 0

        ##
        # BUG #7
        #
        # Jobs still execute after been removed from list
        # verify if row is in remove filter
        ##
        removed = bool(statusIndex.row() in proxyModel.filterConditions["Remove"])
        if removed:
            jobsQueue.statusUpdateSignal.emit(job, JobStatus.Removed)
            continue

        # Check Job Status for Skip
        status = model.dataset[statusIndex.row(), statusIndex.column()]
        if status in [JobStatus.Removed, JobStatus.Skip]:
            jobsQueue.statusUpdateSignal.emit(job, JobStatus.Skipped)
            continue

        jobsQueue.statusUpdateSignal.emit(job, JobStatus.Running)
        cli = RunCommand(
            processLine=displayRunJobs,
            processArgs=[job, output, indexTotal],
            processKWArgs={"funcProgress": funcProgress},
            controlQueue=controlQueue,
            commandShlex=True,
            universalNewLines=False,
            log=log,
        )

        if job.algorithm is None:
            algorithm = config.data.get(config.ConfigKey.Algorithm)
        else:
            algorithm = job.algorithm

        if job.oCommand:
            job.startTime = time()

            if config.data.get(config.ConfigKey.JobsAutoSave):
                job.jobRow[JobKey.Status] = JobStatus.Running
                saveToDb(job)

            dt = datetime.fromtimestamp(job.startTime)

            msg = "*******************\n"
            msg += "Job ID: {} started at {} using algorithm {}.\n\n".format(
                job.jobRow[JobKey.ID], dt.isoformat(), algorithm
            )
            trayIconMessageSignal.emit(
                "Information - MKVBatchMultiplex",
                f"Job ID: {job.jobRow[JobKey.ID]} started.",
                QSystemTrayIcon.Information,
            )
            msgArgs = {"color": SvgColor.cyan}
            output.job.emit(msg, dict(msgArgs))
            job.output.append([msg, dict(msgArgs)])
            exitStatus = "ended"

            if log:
                MODULELOG.debug("RJB0005: Job ID: %s started.", job.jobRow[JobKey.ID])

            updateStatus = True

            if not job.oCommand.commandsGenerated:
                output.job.emit("Generating commands...\n", {"appendEnd": True})
                job.oCommand.generateCommands()

            errorOutputOpen = False

            for (
                index,
                (cmd, baseFiles, sourceFiles, destinationFile, _, _, _),
            ) in enumerate(job.oCommand):
                funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
                #
                # Check Job Status for Abort
                #
                status = model.dataset[statusIndex.row(), statusIndex.column()]

                ###
                # Check controlQueue
                ###
                if controlQueue:
                    queueStatus = controlQueue.popleft()
                    if queueStatus in [
                        JobStatus.Abort,
                        JobStatus.AbortJob,
                        JobStatus.AbortJobError,
                    ]:
                        jobsQueue.statusUpdateSignal.emit(job, JobStatus.Abort)
                        status = JobStatus.Abort
                        exitStatus = queueStatus
                        if queueStatus == JobStatus.Abort:
                            abortAll = True
                        if f := job.oCommand[index - 1][3]:
                            if f.is_file():
                                f.unlink()

                if status == JobStatus.Abort:
                    jobsQueue.statusUpdateSignal.emit(job, JobStatus.Aborted)
                    job.jobRow[JobKey.Status] = JobStatus.Aborted
                    updateStatus = False
                    if exitStatus == "ended":
                        exitStatus = "aborted"
                    job.endTime = time()
                    if config.data.get(config.ConfigKey.JobsAutoSave):
                        job.jobRow[JobKey.Status] = JobStatus.Aborted
                        saveToDb(job, update=True)
                    break

                iVerify.verifyStructure(job.oCommand, index)

                if log:
                    msg = (
                        "Command: {}  Base Files: {} "
                        "Source Files: {} Destination File: {}"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFile)
                    MODULELOG.debug("RJB0006: %s", msg)

                #
                # New Algorithm
                #
                runJob = bool(iVerify)

                if algorithm >= 1:
                    if not iVerify:
                        rc, confidence = mkv.adjustSources(
                            job.oCommand, index, algorithm
                        )
                        runJob = rc
                        if rc:
                            _, shellCommand = job.oCommand.generateCommandByIndex(
                                index, update=True
                            )
                            originalCmd = cmd
                            cmd = shellCommand
                            msg = (
                                f"Warning command adjusted - confidence {confidence}:\n\n"
                                f"Original: {originalCmd}\n"
                                f"     New: {cmd}\n"
                            )
                            if log:
                                MODULELOG.warning("RJB0011: %s", msg)
                        else:
                            msg = (
                                f"Warning command failed adjustment:\n\n"
                                f"Command: {cmd}\n"
                            )
                        if not errorOutputOpen:
                            markErrorOutput(job, output, start=True)
                            errorOutputOpen = True

                        msgArgs = {"color": SvgColor.yellowgreen, "appendEnd": True}
                        output.job.emit(msg, dict(msgArgs))
                        output.error.emit(
                            msg + "\n", dict(msgArgs)
                        )  # hack making it work
                        job.output.append([msg, dict(msgArgs)])
                        job.errors.append(
                            [msg + "\n", dict(msgArgs)]
                        )  # hack making it work
                        if rc:
                            if log:
                                MODULELOG.warning("RJB0011: %s", msg)
                        else:
                            if log:
                                MODULELOG.warning("RJB0012: %s", msg)
                if runJob:
                    ###
                    # Execute cmd
                    ###
                    msg = (
                        "Command: {}\nBase Files: {}\n"
                        "Source Files: {}\nDestination Files: {}\n"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFile)
                    msgArgs = {"appendEnd": True}
                    output.job.emit(msg, dict(msgArgs))

                    if log:
                        MODULELOG.debug("RJB0007: Structure checks ok")

                    if bSimulateRun:
                        dummyRunCommand(funcProgress, indexTotal, controlQueue)
                    else:
                        # TODO: queue to control execution of running job inside
                        # the RunCommand test current configuration
                        cli.command = cmd
                        cli.run()
                else:
                    job.errors.append(iVerify.analysis)
                    totalErrors += 1
                    funcProgress.lblSetValue.emit(4, totalErrors)
                    if not errorOutputOpen:
                        markErrorOutput(job, output, start=True)
                        errorOutputOpen = True
                    msg = "Destination File: {}\nFailed adjustment\n\n".format(
                        destinationFile
                    )
                    msgArgs = {"color": SvgColor.red, "appendEnd": True}
                    output.job.emit(msg, dict(msgArgs))
                    job.output.append([msg, dict(msgArgs)])
                    for i, m in enumerate(iVerify.analysis):
                        if i == 0:
                            lines = m.split("\n")
                            findSource = True
                            for line in lines:
                                color = SvgColor.orange
                                if findSource and (
                                    (searchIndex := line.find("File Name")) >= 0
                                ):
                                    if searchIndex >= 0:
                                        color = SvgColor.tomato
                                        findSource = False
                                msg = line + "\n"
                                msgArgs = {"color": color}
                                output.job.emit(msg, dict(msgArgs))
                                output.error.emit(msg, dict(msgArgs))
                                job.output.append([msg, dict(msgArgs)])
                        else:
                            msgArgs = {"color": SvgColor.red}
                            output.job.emit(m, dict(msgArgs))
                            output.error.emit(m, dict(msgArgs))
                            job.output.append([m, dict(msgArgs)])
                    output.job.emit("\n", {})
                    output.error.emit("\n", {})
                    job.output.append(["\n", {}])
                    job.errors.append(["\n", {}])
                    if log:
                        MODULELOG.error("RJB0008: Structure check failed")
                indexTotal[1] += 100
                indexTotal[0] += 1
                # End for loop for jobs in job.oCommand

            if errorOutputOpen:
                # Mark any error output end
                markErrorOutput(job, output, start=False)
                errorOutputOpen = False

            job.endTime = time()
            dtStart = datetime.fromtimestamp(job.startTime)
            dtEnd = datetime.fromtimestamp(job.endTime)
            dtDuration = dtEnd - dtStart
            msg = "Job ID: {} {} - date {} - running time {}.\n".format(
                job.jobRow[JobKey.ID],
                exitStatus,
                dtEnd.isoformat(),
                strFormatTimeDelta(dtDuration),
            )
            msg += "*******************\n\n\n"
            msgArgs = {"color": SvgColor.cyan, "appendEnd": True}
            output.job.emit(msg, dict(msgArgs))
            job.output.append([msg, dict(msgArgs)])
            msg = "Job ID: {} {}\nruntime {}"
            msg = msg.format(
                job.jobRow[JobKey.ID],
                exitStatus,
                strFormatTimeDelta(dtDuration),
            )
            trayIconMessageSignal.emit(
                "Information - MKVBatchMultiplex",
                msg,
                QSystemTrayIcon.Information,
            )
            if config.data.get(config.ConfigKey.JobHistory):
                if updateStatus:
                    job.jobRow[JobKey.Status] = JobStatus.Done
                saveToDb(job, update=True)
            model.dataset.data[job.jobRowNumber][JobKey.Status].obj = job
            if updateStatus:
                jobsQueue.statusUpdateSignal.emit(job, JobStatus.Done)
            if log:
                MODULELOG.debug("RJB0009: Job ID: %s finished.", job.jobRow[JobKey.ID])
        else:
            totalErrors += 1
            funcProgress.lblSetValue.emit(4, totalErrors)
            msg = "Job ID: {} cannot execute command.\n\nCommand: {}\n"
            msg = msg.format(job.jobRow[JobKey.ID], job.oCommand.command)
            msgArgs = {"color": SvgColor.red}
            output.error.emit(msg, dict(msgArgs))
            job.errors.append([msg, dict(msgArgs)])
            jobsQueue.statusUpdateSignal.emit(job, JobStatus.Error)
            if log:
                MODULELOG.debug(
                    "RJB0010: Job ID: %s cannot execute command: %s.",
                    job.jobRow[JobKey.ID],
                    job.oCommand.command,
                )
    jobsDB.close()
    for index in range(4):
        funcProgress.lblSetValue.emit(index, 0)
    funcProgress.pbSetMaximum.emit(100, 100)
    funcProgress.pbSetValues.emit(0, 100)
    funcProgress.pbReset.emit()
    jobsWorker.running = False

    return "Job queue empty."


def dummyRunCommand(funcProgress, indexTotal, controlQueue):
    """
    dummyRunCommand dummy run job function
    """

    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    i = 0

    while i < 100:
        i += 0.5
        funcProgress.pbSetValues.emit(i, indexTotal[1] + i)
        sleep(0.0001)
        if controlQueue:
            queueStatus = controlQueue.popleft()
            controlQueue.appendleft(queueStatus)
            if queueStatus in [
                JobStatus.Abort,
                JobStatus.AbortJob,
                JobStatus.AbortJobError,
            ]:
                break


def markErrorOutput(job, output, start=True):
    """
    markErrorOutput start/stop messages for error output

    Args:
        **job** (JobInfo): current job

        **output** (OutputWindows): give access to the output widgets

        **start** (bool, optional): signal the start or stop message.
        Defaults to True.
    """

    dt = datetime.fromtimestamp(time())

    if start:
        msg = "---------------------\n"
        msg += "Messages for Job ID: {} started at {}.\n\n".format(
            job.jobRow[JobKey.ID], dt.isoformat()
        )
    else:
        msg = "Messages for Job ID: {} ended at {}.\n\n".format(
            job.jobRow[JobKey.ID], dt.isoformat()
        )
        msg += "---------------------\n"

    msgArgs = {"color": SvgColor.yellow, "appendEnd": True}
    output.error.emit(msg, dict(msgArgs))
    job.errors.append([msg, dict(msgArgs)])


def errorMsg(output, msg, kwargs):

    output.error.emit(msg, kwargs)
    output.job.emit(msg, kwargs)


@staticVars(printPercent=False, counting=False, count=0, line="")
def displayRunJobs(
    ch, job, output, indexTotal, funcProgress=None
):  # pylint: disable=invalid-name
    """
    Convenience function used by jobsWorker to display lines of the mkvmerge
    execution.  The function interprets the input to recognize the lines.
    Also returns the constructed line or None.

    Args:
        ch (str): characters to display
    """

    if ch == "\n":
        displayRunJobs.line += ch
    elif ch == "%":
        displayRunJobs.line += "%"
    else:
        displayRunJobs.line += ch
        return None

    regEx = re.compile(r":\W*(\d+)\%$")
    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    n = -1

    job.output.append([displayRunJobs.line, {}])

    if m := regEx.search(displayRunJobs.line):
        n = int(m.group(1))

    if displayRunJobs.printPercent:
        if displayRunJobs.line == "\n":
            displayRunJobs.line = ""
            return "\n"

    if n >= 0:
        if not displayRunJobs.printPercent:
            # output.job.emit("", {})
            displayRunJobs.printPercent = True
            # job.output.append(["", {}])  # Test Line

        displayRunJobs.line = displayRunJobs.line.strip()

        output.job.emit(displayRunJobs.line, {"replaceLine": True})
        funcProgress.pbSetValues.emit(n, indexTotal[1] + n)
        displayRunJobs.line += "\n"
    else:
        if displayRunJobs.printPercent:
            output.job.emit("\n", {})
            displayRunJobs.printPercent = False
            displayRunJobs.counting = True
            displayRunJobs.count = 0
        if displayRunJobs.counting:
            displayRunJobs.count += 1
        output.job.emit(displayRunJobs.line[:-1], {"appendLine": True})

    if displayRunJobs.count == 2:
        displayRunJobs.count = 0
        displayRunJobs.printPercent = False
        displayRunJobs.counting = False
        output.job.emit("\n\n", {})
        # job.output.append(["\n\n", {}]) hack cannot find the read difference
        job.output.append(["\n", {}])

    # clear proccessed line
    line = displayRunJobs.line
    displayRunJobs.line = ""

    return line
