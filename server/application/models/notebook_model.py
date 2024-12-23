import sqlite3
from server.application.exceptions import (
    DatabaseError,
    ValidationError,
    NotebookNotFoundError,
    DuplicateNotebookError
)

class NotebookModel:
    def __init__(self, db):
        """
        Initialize the NotebookModel with a connection to the database
        :param db: connection to the database
        :raises ValidationError: if the database connection is invalid
        """
        if db is None:
            raise ValidationError("Database connection cannot be None")
        self.db = db

    def create_notebook(self, notebook_name, notebook_path, description):
        """
        Create a new notebook
        :param notebook_name: name of the new notebook
        :param notebook_path: path of the new notebook
        :param description: description of the new notebook
        :raises ValidationError: if the notebook name or the notebook path is empty
        :raises DuplicateNotebookError: if the notebook already exists
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if notebook_name is None:
            raise ValidationError("Notebook name cannot be None")
        if notebook_path is None:
            raise ValidationError("Notebook path cannot be None")
        # Try to create the notebook
        try:
            with self.db.transaction():
                sql = """
                INSERT INTO notebooks (notebook_name, notebook_path, description)
                VALUES (?, ?, ?)
                """
                params = [notebook_name, notebook_path, description]
                self.db.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateNotebookError(f"Note book with name {notebook_name} already exists: {str(e)}")
            raise DatabaseError(f"Failed to create notebook: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to create notebook: {str(e)}")
        
    def get_notebook_id(self, notebook_name):
        """
        Retrieve a notebook's ID by its name
        :param notebook_name: name of the notebook
        :raises ValidationError: if the notebook name is empty
        :raises NotebookNotFoundError: if the notebook dose not exist
        :raises DatabaseError: if database operation fails
        :return: ID of the notebook in database
        """
        if notebook_name is None:
            raise ValidationError("Notebook name cannot be None")
        # Try to get the notebook's ID
        try:
            sql = "SELECT id FROM notebooks WHERE notebook_name = ?"
            result = self.db.fetchone(sql, [notebook_name])
            if result is None:
                raise NotebookNotFoundError(f"Notebook with name {notebook_name} does not exist")
            return result["id"]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get notebook ID: {str(e)}")

    # Use get_notebook_id() before using following methods
    def get_notebook(self, notebook_id):
        """
        Retrieve a notebook's details by its ID
        :param notebook_id: ID of the notebook
        :rasies ValidationError: if the notebook ID is invalid
        :rasies NotbookNotFoundError: if the notebook dose not exist
        :rases DatabaseError: if database operation fails
        :return: dictionary of the notebook in database
        """
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        # Try to get the notebook
        try:
            sql = "SELECT * FROM notebooks WHERE id = ?"
            result =  self.db.fetchone(sql, [notebook_id])
            if result is None:
                raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
            return result
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get notebook: {str(e)}")
        
    def update_notebook(self, notebook_id, new_name=None, new_path=None, new_description=None):
        """
        Update a notebook's details by its ID
        :param notebook_id: ID of the notebook
        :param new_name: new name of the notebook
        :param new_path: new path of the notebook
        :param new_description: new description of the notebook
        :raises ValidationError: if no update parameters provided or invalid notebook ID
        :raises NotebookNotFoundError: if the notebook dose not exist
        :raises DuplicateNotebookError: if the notebook already exists
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        if not any([new_name, new_path, new_description]):
            raise ValidationError("At least one update parameter must be provided")
        # Try to update the notebook
        try:
            # Check whether the notebook exists
            if not self.get_notebook(notebook_id):
                raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
            with self.db.transaction():
                sql = "UPDATE notebooks SET"
                updates = [] # Fields that need to be updated
                params = [] # Parameters for the SQL query
                # Add conditions for fields that need to be updated
                if new_name:
                    updates.append(" notebook_name = ?")
                    params.append(new_name)
                if new_path:
                    updates.append(" notebook_path = ?")
                    params.append(new_path)
                if new_description:
                    updates.append(" description = ?")
                    params.append(new_description)
                # Set update time by CURRENT_TIMESTAMP
                updates.append(" updated_at = CURRENT_TIMESTAMP")
                # Join updates
                sql += ", ".join(updates)
                sql += " WHERE id = ?"
                params.append(notebook_id) 
                # Execute update
                self.db.execute(sql, params)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint" in str(e):
                raise DuplicateNotebookError(f"Notebook with name {new_name} already exists")
            raise DatabaseError(f"Failed to update notebook: {str(e)}")
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to update notebook: {str(e)}")

    def delete_notebook(self, notebook_id):
        """
        Delete a notebook by its ID
        :param notebook_id: ID of the notebook
        :raises ValidationError: if the notebook ID is invalid
        :raises NotebookNotFoundError: if the notebook dose not exist
        :raises DatabaseError: if database operation fails
        :return: NULL
        """
        if not isinstance(notebook_id, int) or notebook_id <= 0:
            raise ValidationError("Invalid notebook ID")
        # Try to delete the notebook
        try:
            # Check whether the notebook exists
            if not self.get_notebook(notebook_id):
                raise NotebookNotFoundError(f"Notebook with ID {notebook_id} does not exist")
            with self.db.transaction():
                sql = "DELETE FROM notebooks WHERE id = ?"
                # Execute delete
                self.db.execute(sql, [notebook_id])
        except (DatabaseError, sqlite3.Error, Exception) as e:
            raise DatabaseError(f"Failed to delete notebook: {str(e)}")

    def get_all_notebooks(self):
        """
        Retrieve all notebooks
        :raises DatabaseError: if database operation fails
        :return: List of all notebooks in database (list of dictionaries)
        """
        try:
            sql = "SELECT * FROM notebooks"
            return self.db.fetchall(sql)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get all notebooks: {str(e)}")