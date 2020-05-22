"""
Classes representing Keys in job related lists
"""
# pylint: disable=too-few-public-methods


class JobsTableKey:
    """
     keys representing the jobs table fields
    """

    rowid = "rowid"
    ID = "id"
    addDate = "addDate"
    addTime = "addTime"
    startTime = "startTime"
    endTime = "endTime"
    job = "job"
    command = "command"
    projectName = "projectName"
    projectInfo = "projectInfo"
    saved = "saved"
    deleteMark = "deleteMark"

    rowidIndex = 0
    IDIndex = 1
    addDateIndex = 2
    addTimeIndex = 3
    startTimeIndex = 4
    endTimeIndex = 5
    jobIndex = 6
    commandIndex = 7
    projectNameIndex = 8
    projectInfoIndex = 9
    savedIndex = 10
    deleteMarkIndex = 11


class JobKey:

    ID = 0
    Status = 1
    Command = 2


class JobHistoryKey:

    ID = 0
    Date = 1
    Status = 2
    Command = 3


class JobStatus:
    """Key values for job related work"""

    Abort = "Abort"
    Aborted = "Aborted"
    AbortForced = "AbortForced"
    AbortJob = "AbortJob"
    AbortJobError = "AbortJobError"
    AddToQueue = "AddToQueue"
    Blocked = "Blocked"
    Done = "Done"
    DoneWithError = "DoneWithError"
    Error = "Error"
    Queue = "Queue"
    Running = "Running"
    Skip = "Skip"
    Skipped = "Skipped"
    Stop = "Stop"
    Stopped = "Stopped"
    Waiting = "Waiting"


def jobStatusTooltip(status):
    """Tooltips for Status column"""

    if not isinstance(status, str):
        return ""

    if JobStatus.Abort == status:
        return "Job has signal to abort execution"
    elif JobStatus.Aborted == status:
        return "Job was aborted"
    elif JobStatus.AbortForced == status:
        return "Job was forced to stop"
    elif JobStatus.AbortJob == status:
        return "Job has signal to abort execution"
    elif JobStatus.AbortJobError == status:
        return "Job was aborted because of an Error"
    elif JobStatus.AddToQueue == status:
        return "Add the job to the Queue"
    elif JobStatus.Blocked == status:
        return "Job is blocked for execution"
    elif JobStatus.Done == status:
        return "Job has ended execution"
    elif JobStatus.DoneWithError == status:
        return "Job has ended execution with some errors"
    elif JobStatus.Error == status:
        return "Error trying to execute job"
    elif JobStatus.Queue == status:
        return "Job is the Queue waiting for execution"
    elif JobStatus.Running == status:
        return "Job is been process by worker"
    elif JobStatus.Skip == status:
        return "Job has a signal for the worker to skip execution"
    elif JobStatus.Skipped == status:
        return "Job was skipped by worker"
    elif JobStatus.Stop == status:
        return "Job has signal to stop execution"
    elif JobStatus.Stopped == status:
        return "Job has stopped execution"
    elif JobStatus.Waiting == status:
        return "Job is waiting to be assigned ID and put on Queue"

    return ""
