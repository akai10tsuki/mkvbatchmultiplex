"""
 Jobs database
"""
from sqlite3 import Error as SQLiteError

from vsutillib.sql import SqlDb


class SqlJobsTable(SqlDb):
    """
    SqlJobsDB sqlite database for jobs history

    Args:
        SqlDb (class): class for managing sqlite connections
    """

    def __init__(self, dbFile=None):

        # initialize local properties
        self.__lastError = None

        # call parent init
        super().__init__(dbFile)

    def _initHelper(self):
        # Create jobs table
        if self.connection is not None:
            self._createJobsTable()

    def _createJobsTable(self):
        # Create jobs table
        if self.connection is not None:
            # version 2.0.0a2

            sqlScript = """
                -- start a transaction
                BEGIN TRANSACTION;

                -- create jobs and dbInfo tables
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER,
                    addDate TEXT,
                    addTime REAL,
                    startTime REAL,
                    endTime REAL,
                    job BLOB,
                    command TEXT,
                    projectName TEXT,
                    projectInfo TEXT,
                    saved INTEGER,
                    deleteMark INTEGER
                );

                CREATE TABLE IF NOT EXISTS dbInfo (
                    dbTable TEXT NOT NULL UNIQUE,
                    version TEXT NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS jobsSearch
                    USING fts5(rowidKey, id, startTime, command);
                """

            self.__lastError = None

            try:
                self.connection.executescript(sqlScript)
                self.commit()
            except SQLiteError as e:
                self.__lastError = "SQLiteError: {}".format(e)
                self.rollback()

            if self.__lastError is None:
                version = self.version("jobs")
                if version is None:
                    self.setVersion("jobs", "2.0.0")

    @property
    def error(self):
        """
        error needed to preserve error status on methods with more than one
            execute commands

        Returns:
            str: value of last error
        """
        if self.__lastError is not None:
            return self.__lastError

        return super().error

    def setVersion(self, *args):
        """
        set table version

        Args:
            dbTable (str): sql table
            version (str): table version
        """

        version = self.version(args[0])

        self.__lastError = None

        if version is None:
            sqlSetVersion = """
                INSERT INTO
                    dbInfo(dbTable, version)
                    VALUES(?, ?)
                """
            self.sqlExecute(sqlSetVersion, *args)
        else:
            sqlSetVersion = """
                UPDATE dbInfo SET
                    version = ?
                    WHERE dbTable = ?;
                """
            self.sqlExecute(sqlSetVersion, args[1], args[0])

    def version(self, dbTable):
        """
        version get table version

        Args:
            dbTable (str): sql table

        Returns:
            str: version of table
        """

        self.__lastError = None

        sqlVersion = "SELECT version FROM dbInfo WHERE dbTable = ?;"

        cursor = self.sqlExecute(sqlVersion, dbTable)

        if cursor:
            row = cursor.fetchone()
            if row:
                return row[0]

        return None

    def connect(self, database, autoCommit=False):
        """override connect to create tables"""
        self.__lastError = None

        rc = super().connect(database, autoCommit)

        self._initHelper()

        return rc

    def delete(self, jobID):
        """
        delete job from database

        Args:
            jobID (int): job id to delete

        Returns:
            sqlite3.cursor: cursor to the database aftter operation
        """

        self.__lastError = None

        cursor = None
        if isinstance(jobID, int):
            sqlDeleteJob = "DELETE FROM jobs WHERE id = ?;"
            cursor = self.sqlExecute(sqlDeleteJob, jobID)
            # if cursor is not None:
            #    self.connection.commit()

        return cursor

    def insert(self, *args):
        """
        insert job into database

        Args:
            jobID (int): job id to insert

        Returns:
            sqlite3.cursor: cursor to the database after operation
        """
        self.__lastError = None

        sqlJob = """ INSERT INTO
                     jobs(id, addDate, addTime, startTime, endTime, job,
                        command, projectName, projectInfo, saved, deleteMark)
                     VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
        cursor = self.sqlExecute(sqlJob, *args)
        if cursor is not None:
            self.connection.commit()
            return cursor.lastrowid

        return 0

    def fetchJob(
        self, jobID, *args, fetchAll=False, whereClause=None, orderClause=None
    ):
        """
        fetchJob fetch information from database by job id

        if jobID is a dict the a WHERE clause with AND will be constructed

        Args:
            jobID (int, dict): WHERE clause AND members and integer implies
                WHERE id = ?
            *args (tuple, optional): tuple with fields. Defaults to None.
            fetchAll (bool, optional): fetch all records in query. Defaults to False.

        Returns:
            sqlite3.cursor: cursor to the operation results
        """

        self.__lastError = None

        fetchFields = ""
        wClause = ""
        values = ""
        if isinstance(jobID, dict):
            strTmp = ""
            wClause = "WHERE "
            totalFields = len(jobID)
            values = []
            for i, (f, v) in enumerate(jobID.items()):
                strTmp += "jobs." + f + " = ?"
                if i < (totalFields - 1):
                    strTmp += " AND "
                values.append(v)
            wClause += strTmp
            if args:
                strTmp = ""
                totalFields = len(args)
                for i, f in enumerate(args):
                    fetchFields += "jobs." + f
                    if i < (totalFields - 1):
                        fetchFields += ", "
            else:
                fetchFields = "jobs.*"
        elif isinstance(jobID, int):
            if jobID <= 0:
                fetchFields = "jobs.*"
                wClause = ""
            else:
                fetchFields = "jobs.*"
                wClause = "WHERE id = ?"
                values = [jobID]

        cursor = None
        if whereClause is not None:
            wClause = whereClause

        sqlFetchID = (
            "SELECT rowid, "
            + fetchFields
            + " FROM jobs"
            + ("" if wClause == "" else " " + wClause)
            + ("" if orderClause is None else " " + orderClause)
            + ";"
        )

        if values:
            cursor = self.sqlExecute(sqlFetchID, *values)
        else:
            cursor = self.sqlExecute(sqlFetchID)

        if fetchAll:
            cursor.fetchall()

        return cursor

    def textSearch(self, searchText):
        """
        textSearch do a full text search on jobs table command field

        Args:
            searchText (str): text to search

        Returns:
            sqlite3.cursor: cursor to the operation results
        """

        if not isinstance(searchText, str):
            return None

        sqlSearch = """
            SELECT rowid, jobs.* FROM jobs
            WHERE rowid IN (
                SELECT rowidKey
                    FROM jobsSearch
                    WHERE jobsSearch MATCH ?);
            """

        cursor = self.sqlExecute(sqlSearch, searchText)

        return cursor

    def deleteJob(self, jobID):
        pass

    def update(self, jobID, fields, *args, whereClause=None):
        """
        update job information on database

        fields = (id, addDate, addTime, startTime, endTime, job)

        Args:
            jobID (int): job id to update
            fields (tuple): fields to update
            args (tuple): values to update
        """

        self.__lastError = None

        wClause = ""
        values = []

        for v in args:
            values.append(v)

        if isinstance(jobID, dict):
            strTmp = ""
            wClause = "WHERE "
            totalFields = len(jobID)
            for i, (f, v) in enumerate(jobID.items()):
                strTmp += f + " = ?"
                if i < (totalFields - 1):
                    strTmp += " AND "
                values.append(v)
            wClause += strTmp
        elif isinstance(jobID, int):
            wClause = "WHERE id = ?"
            values.append(jobID)

        cursor = None
        if whereClause is not None:
            wClause = whereClause

        sqlUpdateJob = "UPDATE jobs SET "
        totalFields = len(fields)
        strTmp = ""

        for i, f in enumerate(fields):
            strTmp += f + " = ?"
            if i < (totalFields - 1):
                strTmp += ", "

        sqlUpdateJob += strTmp + ("" if wClause == "" else " " + wClause) + ";"

        cursor = None

        if values:
            cursor = self.sqlExecute(sqlUpdateJob, *values)

        return cursor


def updateTables(database, fromVersion, toVersion):
    """
    update jobs table form no version to version 2.0.0a1
    """

    sqlScript = ""

    if toVersion == "2.0.0a1" and fromVersion == "":
        sqlScript = """
            -- disable foreign key constraint check
            PRAGMA foreign_keys=off;

            -- start a transaction
            BEGIN TRANSACTION;

            -- Here you can drop column or rename column
            CREATE TABLE IF NOT EXISTS new_jobs_table(
                id INTEGER,
                addDate TEXT,
                addTime REAL,
                startTime REAL,
                endTime REAL,
                job BLOB,
                projectName TEXT,
                projectInfo TEXT,
                saved INTEGER,
                toDelete INTEGER
            );
            -- copy data from the table to the new_table
            INSERT INTO new_jobs_table(id, addDate, addTime, startTime, endTime, job)
                SELECT id, addDate, addTime, startTime, endTime, job
                    FROM jobs;

            -- drop the table
            DROP TABLE jobs;

            -- rename the new_table to the table
            ALTER TABLE new_jobs_table RENAME TO jobs;

            -- set new fields with default values
            UPDATE jobs SET
            projectName = "AutoSaved",
            projectInfo = "AutoSaved",
            saved = 0,
            toDelete = 0;

            -- commit the transaction
            COMMIT;

            -- enable foreign key constraint check
            PRAGMA foreign_keys=on; """

    if toVersion == "2.0.0a2" and fromVersion == "2.0.0a1":
        sqlScript = """
            -- disable foreign key constraint check
            PRAGMA foreign_keys=off;

            -- start a transaction
            BEGIN TRANSACTION;

            -- Here you can drop column or rename column
            CREATE TABLE IF NOT EXISTS new_jobs_table(
                id INTEGER,
                addDate TEXT,
                addTime REAL,
                startTime REAL,
                endTime REAL,
                job BLOB,
                command TEXT,
                projectName TEXT,
                projectInfo TEXT,
                saved INTEGER,
                Deleted INTEGER
            );
            -- copy data from the table to the new_table
            INSERT INTO new_jobs_table(id, addDate, addTime, startTime, endTime, job,
                projectName, projectInfo, saved, Deleted)
            SELECT id, addDate, addTime, startTime, endTime, job, "AutoSaved", "AutoSaved", 0, 0
            FROM jobs;

            -- drop the table
            DROP TABLE jobs;

            -- rename the new_table to the table
            ALTER TABLE new_jobs_table RENAME TO jobs;

            -- set new fields with default values
            UPDATE jobs SET
            command = "";

            -- commit the transaction
            COMMIT;

            -- enable foreign key constraint check
            PRAGMA foreign_keys=on; """

    if sqlScript:
        print("Updating database...")
        cursor = database.connection.cursor()
        cursor.executescript(sqlScript)
