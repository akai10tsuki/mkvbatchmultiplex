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
    """
    Keys for a job row on Jobs Table
    """

    ID = 0
    Status = 1
    Command = 2


class JobHistoryKey:
    """
     Keys for a job in Saved Jobs Table
    """

    ID = 0
    Date = 1
    Status = 2
    Command = 3


class JobStatus:
    """
    Key values for job status and queue control

    Keys:
        **Abort** - abort job worker when running no more jobs on queue will be
        executed can be manually set

        **Aborted** - job has been aborted set by program

        **AbortForced** - jobs has been aboted by program

        **AbortJob** - request abort job by program

        **AbortJobError** - request abort job do to error by program

        **AddToQueue** - add job to queue set by program

        **Blocked** - job is blocked from execution set by program

        **Done** - job has finished execution set by program

        **DoneWithError** - job finished with errors set by program

        **Error** - error found when trying to execute job

        **Queue** - job in queue waiting for execution

        **Remove** - remove job from Jobs Table set in context menu

        **Removed** - job removed from Jobs Table set by program

        **Running** - job is running set by program

        **Skip** - skip job when is time to execute can be set by user

        **Skipped** - job skipped

        **Stop** - stop running job  can be set by user if job is Running

        **Stopped** - job stopped from execution set by program

        **Waiting** - job waiting to be added to queue if removed from queue or no
        job ID assigned
    """

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
    Remove = "Remove"
    Removed = "Removed"
    Running = "Running"
    Skip = "Skip"
    Skipped = "Skipped"
    Stop = "Stop"
    Stopped = "Stopped"
    Waiting = "Waiting"


def jobStatusTooltip(status):
    """
    Tooltips for Status column
    """

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
