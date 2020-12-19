"""
jobsDB
"""

try:
    import cPickle as pickle
except:  # pylint: disable=bare-except
    import pickle
import sys
import zlib

from .. import config

from .JobKeys import JobKey, JobsTableKey
from .SqlJobsTable import SqlJobsTable

def saveToDb(job, update=False, name=None, description=None):
    """
    saveToDb add the job to the history database

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
        if name is None:
            jobName = "AutoSave"
        else:
            jobName = name
        if description is None:
            jobDescription = "AutoSave"
        else:
            jobDescription = description
        jobsDB = SqlJobsTable(config.data.get(config.ConfigKey.SystemDB))
        cmpJob = zlib.compress(pickle.dumps(job))
        if not update:
            rowid = jobsDB.insert(
                job.jobRow[JobKey.ID],
                job.date.isoformat(),
                job.addTime,
                job.startTime,
                job.endTime,
                cmpJob,
                job.oCommand.command,
                jobName,
                jobDescription,
                0,
                0,
            )
            rc = rowid

            if rowid > 0:
                sqlSearchUpdate = """
                    INSERT INTO jobsSearch(rowidKey, id, startTime, command)
                        VALUES(?, ?, ?, ?); """
                jobsDB.sqlExecute(
                    sqlSearchUpdate,
                    rowid,
                    job.jobRow[JobKey.ID],
                    job.startTime,
                    job.oCommand.command,
                )
            if rowid == 0:
                print("error", jobsDB.error)
                sys.exit()
        else:
            # jobsDB.update(449, (JobsTableKey.startTime, ), 80)
            jobsDB.update(
                job.jobRow[JobKey.ID],
                (JobsTableKey.startTime, JobsTableKey.endTime, JobsTableKey.job),
                job.startTime,
                job.endTime,
                cmpJob,
            )
        jobsDB.close()

    return rc



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

def removeFromDb(database, recordID, jobID, update=False):
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
        if not update:
            rowid = database.delete(
                jobID,
            )
            rc = rowid

    return rc
