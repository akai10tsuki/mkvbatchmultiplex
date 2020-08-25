"""
jobsWorker
"""

import logging

try:
    import cPickle as pickle
except:  # pylint: disable=bare-except
    import pickle
import re
import sys
import zlib

from datetime import datetime
from time import time, sleep

from PySide2.QtWidgets import QSystemTrayIcon

import vsutillib.mkv as mkv

from vsutillib.misc import staticVars, strFormatTimeDelta
from vsutillib.process import RunCommand
from vsutillib.pyqt import SvgColor

from .. import config

from .jobKeys import JobStatus, JobKey, JobsTableKey
from .SqlJobsTable import SqlJobsTable


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


@staticVars(running=False)
def jobsWorker(
    jobQueue,
    output,
    model,
    funcProgress,
    controlQueue,
    trayIconMessageSignal,
    log=False,
):
    """
    jobsWorker execute jobs on queue

    Args:
        jobQueue (JobQueue): Job queue has all related information for the job
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
    totalJobs = len(jobQueue)
    remainingJobs = totalJobs - 1
    currentJob = 0
    indexTotal = [0, 0]
    verify = mkv.VerifyStructure(log=log)
    totalErrors = funcProgress.lbl[4]
    abortAll = False
    bSimulateRun = config.data.get(config.ConfigKey.SimulateRun)

    while job := jobQueue.popLeft():

        # job = copy.deepcopy(qJob)

        job.jobRow = model.dataset[
            job.jobRowNumber,
        ]
        statusIndex = model.index(job.jobRowNumber, JobKey.Status)

        if abortAll:
            jobQueue.statusUpdateSignal.emit(job, JobStatus.Aborted)
            continue

        actualRemaining = len(jobQueue)

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

        # Check Job Status for Skip
        #
        # sourceIndex = job.statusIndex
        status = model.dataset[statusIndex.row(), statusIndex.column()]

        if status == JobStatus.Skip:
            jobQueue.statusUpdateSignal.emit(job, JobStatus.Skipped)
            continue
        #
        # Check Job Status for Skip

        jobQueue.statusUpdateSignal.emit(job, JobStatus.Running)
        cli = RunCommand(
            processLine=displayRunJobs,
            processArgs=[job, output, indexTotal],
            processKWArgs={"funcProgress": funcProgress},
            controlQueue=controlQueue,
            commandShlex=True,
            universalNewLines=True,
            log=log,
        )

        if job.oCommand:
            job.startTime = time()

            if config.data.get(config.ConfigKey.JobHistory):
                job.jobRow[JobKey.Status] = JobStatus.Running
                addToDb(jobsDB, job)

            dt = datetime.fromtimestamp(job.startTime)

            msg = "*******************\n"
            msg += "Job ID: {} started at {}.\n\n".format(
                job.jobRow[JobKey.ID], dt.isoformat()
            )
            trayIconMessageSignal.emit(
                "Information - MKVBatchMultiplex",
                f"Job ID: {job.jobRow[JobKey.ID]} started.",
                QSystemTrayIcon.Information,
            )
            output.job.emit(msg, {"color": SvgColor.cyan})
            exitStatus = "ended"

            if log:
                MODULELOG.debug("RJB0005: Job ID: %s started.", job.jobRow[JobKey.ID])

            updateStatus = True

            if not job.oCommand.commandsGenerated:
                output.job.emit("Generating commands...\n", {"appendEnd": True})
                job.oCommand.generateCommands()

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
                        jobQueue.statusUpdateSignal.emit(job, JobStatus.Abort)
                        status = JobStatus.Abort
                        exitStatus = queueStatus
                        if queueStatus == JobStatus.Abort:
                            abortAll = True
                        if f := job.oCommand[index - 1][3]:
                            if f.is_file():
                                f.unlink()

                if status == JobStatus.Abort:
                    jobQueue.statusUpdateSignal.emit(job, JobStatus.Aborted)
                    job.jobRow[JobKey.Status] = JobStatus.Aborted
                    updateStatus = False
                    if exitStatus == "ended":
                        exitStatus = "aborted"
                    job.endTime = time()
                    if config.data.get(config.ConfigKey.JobHistory):
                        job.jobRow[JobKey.Status] = JobStatus.Aborted
                        addToDb(jobsDB, job, update=True)
                    break

                verify.verifyStructure(baseFiles, sourceFiles, destinationFile)

                if log:
                    msg = (
                        "Command: {}  Base Files: {} "
                        "Source Files: {} Destination File: {}"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFile)
                    MODULELOG.debug("RJB0006: %s", msg)

                if verify:
                    ###
                    # Execute cmd
                    ###
                    msg = (
                        "Command: {}\nBase Files: {}\n"
                        "Source Files: {}\nDestination Files: {}\n"
                    )
                    msg = msg.format(cmd, baseFiles, sourceFiles, destinationFile)
                    output.job.emit(msg, {"appendEnd": True})

                    if log:
                        MODULELOG.debug("RJB0007: Structure checks ok")

                    if bSimulateRun:
                        dummyRunCommand(funcProgress, indexTotal, controlQueue)
                    else:
                        # TODO: queue to control execution of running job inside
                        # the RunCommand
                        cli.command = cmd
                        cli.run()

                else:
                    job.errors.append(verify.analysis)
                    totalErrors += 1
                    funcProgress.lblSetValue.emit(4, totalErrors)

                    msg = "Error Job ID: {} ---------------------\n\n".format(
                        job.jobRow[JobKey.ID]
                    )
                    output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})
                    msg = "Destination File: {}\n\n".format(destinationFile)
                    job.output.append(msg)
                    output.job.emit(msg, {"color": SvgColor.red, "appendEnd": True})
                    # output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})

                    for i, m in enumerate(verify.analysis):
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
                                output.job.emit(line + "\n", {"color": color})
                                output.error.emit(line + "\n", {"color": color})
                                job.output.append(line + "\n")
                        else:
                            output.job.emit(m, {"color": SvgColor.red})
                            job.output.append(m + "\n")
                            output.error.emit(m, {"color": SvgColor.red})

                    job.output.append("\n")
                    # output.job.emit("", {"appendEnd": True})
                    msg = "Error Job ID: {} ---------------------\n\n".format(
                        job.jobRow[JobKey.ID]
                    )
                    output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})

                    if log:
                        MODULELOG.error("RJB0008: Structure check failed")

                indexTotal[1] += 100
                indexTotal[0] += 1

                # End for loop for jobs in job.oCommand

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
            job.output.append(msg)
            msg += "*******************\n\n\n"
            output.job.emit(msg, {"color": SvgColor.cyan, "appendEnd": True})

            msg = "Job ID: {} {}\nruntime {}"
            msg = msg.format(
                job.jobRow[JobKey.ID], exitStatus, strFormatTimeDelta(dtDuration),
            )
            trayIconMessageSignal.emit(
                "Information - MKVBatchMultiplex", msg, QSystemTrayIcon.Information,
            )

            if config.data.get(config.ConfigKey.JobHistory):
                if updateStatus:
                    job.jobRow[JobKey.Status] = JobStatus.Done
                addToDb(jobsDB, job, update=True)

            if updateStatus:
                jobQueue.statusUpdateSignal.emit(job, JobStatus.Done)

            if log:
                MODULELOG.debug("RJB0009: Job ID: %s finished.", job.jobRow[JobKey.ID])

        else:
            totalErrors += 1
            funcProgress.lblSetValue.emit(4, totalErrors)
            msg = "Job ID: {} cannot execute command.\n\nCommand: {}\n"
            msg = msg.format(job.jobRow[JobKey.ID], job.oCommand.command)
            output.error.emit(msg, {"color": SvgColor.red})
            jobQueue.statusUpdateSignal.emit(job, JobStatus.Error)

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


def addToDb(database, job, update=False):
    """
    addToDb add the job to the history database

    Args:
        database (SqlJobsTable): history database
        job (JobInfo): running job information
        update (bool, optional): update is true if record should exits.
            Defaults to False.

    Returns:
        int: rowid if insert successful. 0 otherwise.
    """

    # Compress job information:
    # compressed = zlib.compress(cPickle.dumps(obj))

    # Get it back:
    # obj = cPickle.loads(zlib.decompress(compressed))

    # Key ID, startTime
    #

    bSimulateRun = config.data.get(config.ConfigKey.SimulateRun)
    rc = 0

    if not bSimulateRun:
        cmpJob = zlib.compress(pickle.dumps(job))
        if not update:
            rowid = database.insert(
                job.jobRow[JobKey.ID],
                job.date.isoformat(),
                job.addTime,
                job.startTime,
                job.endTime,
                cmpJob,
                job.oCommand.command,
                "AutoSaved",
                "AutoSaved",
                0,
                0,
            )
            rc = rowid

            if rowid > 0:
                sqlSearchUpdate = """
                    INSERT INTO jobsSearch(rowidKey, id, startTime, command)
                        VALUES(?, ?, ?, ?); """
                database.sqlExecute(
                    sqlSearchUpdate,
                    rowid,
                    job.jobRow[JobKey.ID],
                    job.startTime,
                    job.oCommand.command,
                )
            if rowid == 0:
                print("error", database.error)
                sys.exit()
        else:
            # jobsDB.update(449, (JobsTableKey.startTime, ), 80)
            database.update(
                job.jobRow[JobKey.ID],
                (JobsTableKey.startTime, JobsTableKey.endTime, JobsTableKey.job),
                job.startTime,
                job.endTime,
                cmpJob,
            )

    return rc


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


def errorMsg(output, msg, kwargs):

    output.error.emit(msg, kwargs)
    output.job.emit(msg, kwargs)


@staticVars(printPercent=False, counting=False, count=0)
def displayRunJobs(line, job, output, indexTotal, funcProgress=None):
    """
    Convenience function used by jobsWorker
    to display lines of the mkvmerge
    execution

    Args:
        line (str): line to display
    """

    regEx = re.compile(r":\W*(\d+)%$")
    funcProgress.lblSetValue.emit(2, indexTotal[0] + 1)
    n = -1

    job.output.append(line)

    if m := regEx.search(line):
        n = int(m.group(1))

    if n >= 0:
        if not displayRunJobs.printPercent:
            output.job.emit("\n", {})
            displayRunJobs.printPercent = True
            job.output.append("")

        output.job.emit(line[:-1], {"replaceLine": True})
        funcProgress.pbSetValues.emit(n, indexTotal[1] + n)

    else:
        if displayRunJobs.printPercent:
            # output.job.emit("\n", {})
            displayRunJobs.printPercent = False
            displayRunJobs.counting = True
            displayRunJobs.count = 0
        if displayRunJobs.counting:
            displayRunJobs.count += 1

        output.job.emit(line[:-1], {"appendLine": True})

    # if (line.find("El multiplexado") == 0) or (line.find("Multiplexing took") == 0):
    if displayRunJobs.count == 3:
        displayRunJobs.count = 0
        displayRunJobs.printPercent = False
        displayRunJobs.counting = False
        output.job.emit("\n\n", {})
        job.output.append("\n\n")
