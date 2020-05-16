"""
 Jobs database
"""

from vsutillib.sql import SqlDb

class JobsDB(SqlDb):
    def __init__(self, dbFile=None):
        super().__init__(dbFile)

    def _initHelper(self):

        # Create jobs table
        if self.connection is not None:
            sqlJobsTable = """ CREATE TABLE IF NOT EXISTS jobs (
                                id integer PRIMARY KEY,
                                addDate text,
                                addTime REAL,
                                startTime REAL,
                                endTime REAL,
                                job BLOB
                                ) """
            self.sqlExecute(sqlJobsTable)
            print("create table")

    def connect(self, database, autoCommit=False):
        super().connect(database, autoCommit)

        self._initHelper()

    def delete(self, jobID):

        cursor = None
        if isinstance(jobID, int):
            sqlDeleteJob = "DELETE FROM jobs WHERE id=?"
            cursor = self.sqlExecute(sqlDeleteJob, jobID)
            if cursor is not None:
                self.connection.commit()

        return cursor

    def insert(self, *args):

        sqlJob = """ INSERT INTO
                     jobs(id, addDate, addTime, startTime, endTime, job)
                     VALUES(?, ?, ?, ?, ?, ?) """
        cursor = self.sqlExecute(sqlJob, *args)
        if cursor is not None:
            self.connection.commit()

        return cursor

    def fetchJob(self, jobID, fields=None, fetchAll=False):
        """
        fetchJob fetch information from database by job id

        Args:
            jobID (int): job identification number
            fields (tuple, optional): tuple with fields. Defaults to None.
            fetchAll (bool, optional): fetch all records in query. Defaults to False.

        Returns:
            [type]: [description]
        """

        cursor = None
        if isinstance(jobID, int):

            if jobID <= 0:
                sqlFechID = "SELECT * FROM jobs"
                cursor = self.sqlExecute(sqlFechID)
            else:
                sqlFechID = "SELECT * FROM jobs WHERE id=?"
                cursor = self.sqlExecute(sqlFechID, jobID)

            if fetchAll:
                cursor.fetchall()

        return cursor
