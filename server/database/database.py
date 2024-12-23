from pathlib import Path
import sqlite3
from contextlib import contextmanager
from server.application.exceptions import DatabaseError

class Database:
    def __init__(self, repository_name, base_path = '.'):
        """
        Initialize the database object
        :param repository_name: name of the notebook repository
        :base_path: the path containing all notebooks and notes
        """
        # Path of the database file (attention that the name of database file is fixed)
        self.__db_path = Path(__file__).parent / f"{repository_name}.db"
        # Connection to the database
        self.__connection = None
        # The cursor of the database
        self.__cursor = None
        # Base path
        self.__base_path = base_path
        # Execute initialization
        self.initialize()

    def connect(self):
        """
        Connect to the database
        """
        # Database file will be created if it does not exist
        self.__connection = sqlite3.connect(self.__db_path)
        # Return by sqlite3.Row
        self.__connection.row_factory = sqlite3.Row
        self.__cursor = self.__connection.cursor()

    def close(self):
        """
        Close the database
        """
        if not self.__connection:
            raise DatabaseError("Database connection is not initialized")
        self.__connection.close()

    def commit(self):
        """
        Commit changes to the database
        """
        if not self.__connection:
            raise DatabaseError("Database connection is not initialized")
        self.__connection.commit()

    def execute(self, sql, params=None):
        """
        Execute a SQL statement on the database
        :param sql: sql statement to be executed
        :param params: parameters to be passed into the sql statement
        :return: None
        """
        if not self.__cursor:
            raise DatabaseError("Cursor is not initialized. Please check the database connection")
        if params is None:
            params = []
        # Execute the SQL statement
        self.__cursor.execute(sql, params)
        # Commit changes
        self.commit()

    def fetchone(self, sql, params=None):
        """
        Fetch one row from the query result
        :param sql: sql statement to be executed
        :param params: parameters to be passed into the sql statement
        :return: dictionary of the result, if nothing matches the sql statement, return None
        """
        if not self.__cursor:
            raise DatabaseError("Cursor is not initialized. Please check the database connection")
        if params is None:
            params = []
        self.__cursor.execute(sql, params)
        result = self.__cursor.fetchone()
        # If the result is not None, convert it to a dictionary
        return dict(result) if result else None

    def fetchall(self, sql, params=None):
        """
        Fetch all rows from the query result
        :param sql: sql statement to be executed
        :param params: parameters to be passed into the sql statement
        :return: a list of dictionaries, each dictionary is one row of the result
        """
        if not self.__cursor:
            raise DatabaseError("Cursor is not initialized. Please check the database connection")
        if params is None:
            params = []
        self.__cursor.execute(sql, params)
        # Return list of dictionaries
        return [dict(result) for result in self.__cursor.fetchall()]
        
    def initialize(self):
        """
        Initialize the database
        :return: None
        """
        self.connect()
        self.create_tables()
        self.crete_indices()

    def create_tables(self):
        """
        Create the tables in the database
        :return: None
        """
        # Create table of notebooks
        create_notebooks_table = """
            CREATE TABLE IF NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY,
                notebook_name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        # Create table of notes, notebook_id is a foreign key
        create_notes_table = """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                notebook_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (notebook_id) REFERENCES notebooks (id) ON DELETE CASCADE
                UNIQUE (title, notebook_id)
            )
        """
        # Create table of tags
        create_tags_table = """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                tag_name TEXT NOT NULL UNIQUE
            )
        """
        # Create association table for notes and tags
        create_note_tags_table = """
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        """
        # Execute creation
        self.execute(create_notebooks_table)
        self.execute(create_notes_table)
        self.execute(create_tags_table)
        self.execute(create_note_tags_table)

    def crete_indices(self):
        """
        Create indices of the tables in the database
        :return: None
        """
        create_notebook_index = "CREATE INDEX IF NOT EXISTS notebook_name_idx ON notebooks (notebook_name)"
        create_note_index = "CREATE INDEX IF NOT EXISTS title_idx ON notes (title)"
        create_tag_index = "CREATE INDEX IF NOT EXISTS tag_name_idx ON tags (tag_name)"
        # Execute creation of indices
        self.execute(create_notebook_index)
        self.execute(create_note_index)
        self.execute(create_tag_index)

    def update_record(self, table, data, conditions):
        """
        Update a record in the database
        :param table: name of the table to be updated
        :param data: a dictionary with the data to be updated
        :param conditions: a dictionary with the conditions determine which record should be updated
        :return: None
        """
        # Construct the SQL statement
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        where_clause = " AND ".join([f"{key} = ?" for key in conditions.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(conditions.values())
        # Execute update
        self.execute(sql, params)

    def begin_transaction(self):
        """
        Begin a transaction
        :return: None
        """
        # Disable auto-commit
        self.__connection.isolation_level = None
        # Begin a transaction
        self.__cursor.execute("BEGIN;")

    def commit_transaction(self):
        """
        Commit a transaction
        :return: None
        """
        # Enable auto-commit
        self.__connection.isolation_level = ''
        self.__connection.commit()

    def rollback_transaction(self):
        """
        Rollback a transaction
        :return: None
        """
        self.__connection.rollback()
        
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions
        :return: None
        """
        # Checking conditions before beginning a transaction
        if not self.__connection:
            raise DatabaseError("Database connection is not initialized")
        if not self.__cursor:
            raise DatabaseError("Cursor is not initialized. Please check the database connection")
        try:
            # Begin a transaction
            self.begin_transaction()
            yield # Back to the with block to execute sql operations
            # Commit if successful, other wise jump to the except block
            self.commit_transaction()
        except Exception:
            # Rollback if an error occurs
            self.rollback_transaction()
            raise # Raise the error
        
    def get_base_path(self):
        """
        Get the base path
        :return: base path
        """
        return self.__base_path
