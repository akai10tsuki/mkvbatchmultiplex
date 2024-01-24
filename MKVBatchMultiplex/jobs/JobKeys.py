"""
Classes representing Keys in job related lists
"""
# pylint: disable=too-few-public-methods


class JobsTableKey:
    """
     keys representing the jobs table fields
    """

    rowid: str = "rowid"
    ID: str = "id"
    addDate: str = "addDate"
    addTime: str = "addTime"
    startTime: str = "startTime"
    endTime: str = "endTime"
    job: str = "job"
    command: str = "command"
    projectName: str = "projectName"
    projectInfo: str = "projectInfo"
    saved: str = "saved"
    deleteMark: str = "deleteMark"

    rowidIndex: int = 0
    IDIndex: int = 1
    addDateIndex: int = 2
    addTimeIndex: int = 3
    startTimeIndex: int = 4
    endTimeIndex: int = 5
    jobIndex: int = 6
    commandIndex: int = 7
    projectNameIndex: int = 8
    projectInfoIndex: int = 9
    savedIndex: int = 10
    deleteMarkIndex: int = 11


class JobKey:
    """
    Keys for a job row on Jobs Table
    """

    ID: int = 0
    Status: int = 1
    Command: int = 2


class JobHistoryKey:
    """
     Keys for a job in Saved Jobs Table
    """

    ID: int = 0
    Date: int = 1
    Status: int = 2
    Command: int = 3


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

    Abort: str = "Abort"
    Aborted: str = "Aborted"
    AbortForced: str = "AbortForced"
    AbortJob: str = "AbortJob"
    AbortJobError: str = "AbortJobError"
    AddToQueue: str = "AddToQueue"
    Blocked: str = "Blocked"
    Done: str = "Done"
    DoneWithError: str = "DoneWithError"
    Error: str = "Error"
    Queue: str = "Queue"
    Remove: str = "Remove"
    Removed: str = "Removed"
    Running: str = "Running"
    Skip: str = "Skip"
    Skipped: str = "Skipped"
    Stop: str = "Stop"
    Stopped: str = "Stopped"
    Waiting: str = "Waiting"


def jobStatusTooltip(status: JobStatus) -> str:
    """
    Tooltips for Status column
    """

    if not isinstance(status, str):
        return ""

    match status:
        case JobStatus.Abort:
            return "Job has signal to abort execution"
        case JobStatus.Aborted:
            return "Job was aborted"
        case JobStatus.AbortForced:
            return "Job was forced to stop"
        case JobStatus.AbortJob:
            return "Job has signal to abort execution"
        case JobStatus.AbortJobError:
            return "Job was aborted because of an Error"
        case JobStatus.AddToQueue:
            return "Add the job to the Queue"
        case JobStatus.Blocked:
            return "Job is blocked for execution"
        case JobStatus.Done:
            return "Job has ended execution"
        case JobStatus.DoneWithError:
            return "Job has ended execution with some errors"
        case JobStatus.Error:
            return "Error trying to execute job"
        case JobStatus.Queue:
            return "Job is the Queue waiting for execution"
        case JobStatus.Running:
            return "Job is been process by worker"
        case JobStatus.Skip:
            return "Job has a signal for the worker to skip execution"
        case JobStatus.Skipped:
            return "Job was skipped by worker"
        case JobStatus.Stop:
            return "Job has signal to stop execution"
        case JobStatus.Stopped:
            return "Job has stopped execution"
        case JobStatus.Waiting:
            return "Job is waiting to be assigned ID and put on Queue"
        case _:
            return ""
