"""
Class to process jobs queue
"""
# RJB0011

import copy
import logging

try:
    import cPickle as pickle
except:
    import pickle
import re
import zlib

# import threading
from time import sleep, time
from datetime import datetime, timedelta

from PySide2.QtCore import QObject, QModelIndex, Qt, Signal

import vsutillib.mkv as mkv

from vsutillib.process import ThreadWorker, RunCommand, isThreadRunning
from vsutillib.pyqt import SvgColor
from vsutillib.misc import staticVars

from .. import config
from ..models import TableProxyModel
from .jobKeys import JobStatus, JobKey, JobsTableKey
from .SqlJobsTable import SqlJobsTable


MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class RunJobs(QObject):
    """
    run test run worker thread
    """

    finishedSignal = Signal()
    startSignal = Signal()
    resultSignal = Signal(object)

    # Class logging state
    __log = False

    @classmethod
    def classLog(cls, setLogging=None):
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    def __init__(
        self,
        parent,
        jobsQueue=None,
        progressFunc=None,
        proxyModel=None,
        controlQueue=None,
        log=None,
    ):
        super(RunJobs, self).__init__()

        self.__jobsQueue = None
        self.__logging = False
        self.__output = None
        self.__process = None
        self.__progress = None
        self.__proxyModel = None
        self.__model = None

        self.parent = parent
        self.jobsqueue = jobsQueue
        self.progress = progressFunc
        self.proxyModel = proxyModel
        self.controlQueue = controlQueue
        self.mainWindow = self.parent.parent
        self.jobsWorker = None
        self.log = log

    @property
    def log(self):
        """
        class property can be used to override the class global
        logging setting

            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return RunJobs.classLog()

    @log.setter
    def log(self, value):
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    @property
    def running(self):
        return isThreadRunning(config.WORKERTHREADNAME)

    @property
    def jobsqueue(self):
        return self.__jobsQueue

    @jobsqueue.setter
    def jobsqueue(self, value):
        self.__jobsQueue = value

    @property
    def model(self):
        return self.__model

    @property
    def proxyModel(self):
        return self.__proxyModel

    @proxyModel.setter
    def proxyModel(self, value):
        if isinstance(value, TableProxyModel):
            self.__proxyModel = value
            self.__model = value.sourceModel()

    @property
    def output(self):
        return self.__output

    @output.setter
    def output(self, value):
        self.__output = value

    @property
    def process(self):
        return self.__process

    @process.setter
    def process(self, value):
        self.__process = value

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, value):
        self.__progress = value

    def run(self):
        """
        run summit jobs to worker
        """

        if self.jobsqueue and not self.running:
            self.jobsWorker = ThreadWorker(
                runJobs,
                self.jobsqueue,
                self.output,
                self.model,
                self.progress,
                self.controlQueue,
                log=self.log,
                funcStart=self.start,
                funcResult=self.result,
                funcFinished=self.finished,
            )
            self.jobsWorker.name = config.WORKERTHREADNAME
            self.jobsWorker.start()

            return True

        if not self.jobsqueue:
            msg = "Jobs Queue empty"
            self.output.error.emit(msg, {"color": SvgColor.yellow})

            if self.log:
                MODULELOG.error("RJB0001: Error: %s", msg)

        if self.running:
            msg = "Jobs running"
            self.output.error.emit(msg, {"color": SvgColor.yellow})

            if self.log:
                MODULELOG.error("RJB0002: Error: %s", msg)

        return False

    def start(self):
        """
        start generate signal for start of run
        """

        self.startSignal.emit()

        if self.log:
            MODULELOG.debug("RJB0003: Jobs started.")

    def finished(self):
        """
        finished generate signal for finished run
        """

        self.finishedSignal.emit()

        if self.log:
            MODULELOG.debug("RJB0004: Jobs finished.")

    def result(self, funcResult):
        """
        result from jobs queue process

        Args:
            funcResult (str): messages from runJobs
        """

        self.resultSignal.emit(funcResult)


@staticVars(printPercent=False)
def displayRunJobs(line, job, output, indexTotal, funcProgress=None):
    """
    Convenience function used by runJobs
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

        output.job.emit(line[:-1], {"appendLine": True})

    if (line.find("El multiplexado") == 0) or (line.find("Multiplexing took") == 0):
        output.job.emit("\n\n\n", {})
        job.output.append("\n\n")


@staticVars(running=False)
def runJobs(jobQueue, output, model, funcProgress, controlQueue, log=False):
    """
    runJobs execute jobs on queue

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

    if runJobs.running:
        # Block direct calls while working there should be none
        return "Working..."

    runJobs.running = True
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

        job.jobRow = model.dataset[job.jobRowNumber,]
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
        #sourceIndex = job.statusIndex
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

        historyOn = False

        if job.oCommand:
            job.startTime = time()

            if config.data.get(config.ConfigKey.JobHistory):
                job.jobRow[JobKey.Status] = model.dataset[statusIndex.row(), statusIndex.column()]
                addToDb(jobsDB, job)

            dt = datetime.fromtimestamp(job.startTime)

            msg = "*******************\n"
            msg += "Job ID: {} started at {}.\n\n".format(
                job.jobRow[JobKey.ID], dt.isoformat()
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
                    #output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})

                    for i, m in enumerate(verify.analysis):
                        if i == 0:
                            lines = m.split("\n")
                            findSource = True
                            for index, line in enumerate(lines):
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
                    #output.job.emit("", {"appendEnd": True})
                    msg = "Error Job ID: {} ---------------------\n\n".format(
                        job.jobRow[JobKey.ID]
                    )
                    output.error.emit(msg, {"color": SvgColor.red, "appendEnd": True})

                    if log:
                        MODULELOG.error("RJB0008: Structure check failed")

                indexTotal[1] += 100
                indexTotal[0] += 1

            job.endTime = time()
            if config.data.get(config.ConfigKey.JobHistory):
                job.jobRow[JobKey.Status] = JobStatus.Done
                addToDb(jobsDB, job, update=True)

            dtStart = datetime.fromtimestamp(job.startTime)
            dtEnd = datetime.fromtimestamp(job.endTime)

            dtDuration = dtEnd - dtStart

            msg = "\nJob ID: {} {} - ended at {} - running time {}.\n".format(
                job.jobRow[JobKey.ID],
                exitStatus,
                dtEnd.isoformat(),
                dtDuration,
            )
            msg += "*******************\n\n\n"
            output.job.emit(msg, {"color": SvgColor.cyan, "appendEnd": True})

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
    runJobs.running = False

    return "Job queue empty."


def addToDb(db, job, update=False):

    cmpJob = zlib.compress(pickle.dumps(job))

    # Compress:
    # compressed = zlib.compress(cPickle.dumps(obj))

    # Get it back:
    # obj = cPickle.loads(zlib.decompress(compressed))

    if not update:
        db.insert(
            job.jobRow[JobKey.ID],
            job.date.isoformat(),
            job.addTime,
            job.startTime,
            job.endTime,
            cmpJob,
        )
    else:
        # jobsDB.update(449, (JobsTableKey.startTime, ), 80)
        db.update(
            job.jobRow[JobKey.ID],
            (JobsTableKey.startTime, JobsTableKey.endTime, JobsTableKey.job),
            job.startTime,
            job.endTime,
            cmpJob,
        )


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
