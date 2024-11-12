class NotebookModel:
    def __init__(self, db):
        """
        Initialize the NotebookModel with a connection to the database
        :param db: connection to the database
        """
        self.db = db

    def create_notebook(self, notebook_name, notebook_path, description):
        """
        Create a new notebook
        :param notebook_name: name of the new notebook
        :param notebook_path: path of the new notebook
        :param description: description of the new notebook
        :return: NULL
        """
        sql = """
        INSERT INTO notebooks (notebook_name, notebook_path, description)
        VALUES (?, ?, ?)
        """
        params = [notebook_name, notebook_path, description]
        self.db.execute(sql, params)

    def get_notebook_id(self, notebook_name):
        """
        Retrieve a notebook's ID by its name
        :param notebook_name: name of the notebook
        :return: ID of the notebook in database
        """
        sql = "SELECT id FROM notebooks WHERE notebook_name = ?"
        result = self.db.fetchone(sql, [notebook_name])
        return result["id"] if result else None

    # Use get_notebook_id() before using following methods
    def get_notebook(self, notebook_id):
        """
        Retrieve a notebook's details by its ID
        :param notebook_id: ID of the notebook
        :return: row of the notebook in database
        """
        sql = "SELECT * FROM notebooks WHERE id = ?"
        return self.db.fetchone(sql, [notebook_id])

    def update_notebook(self, notebook_id, new_name=None, new_path=None, new_description=None):
        """
        Update a notebook's details by its ID
        :param notebook_id: ID of the notebook
        :param new_name: new name of the notebook
        :param new_path: new path of the notebook
        :param new_description: new description of the notebook
        :return: NULL
        """
        sql = "UPDATE notebooks SET"
        params = []
        # Add conditions for fields that need to be updated
        if new_name:
            sql += " notebook_name = ?,"
            params.append(new_name)
        if new_path:
            sql += " notebook_path = ?,"
            params.append(new_path)
        if new_description:
            sql += " description = ?,"
            params.append(new_description)
        # Set update time by CURRENT_TIMESTAMP
        sql += " updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params.append(notebook_id)
        # Execute update
        self.db.execute(sql, params)

    def delete_notebook(self, notebook_id):
        """
        Delete a notebook by its ID
        :param notebook_id: ID of the notebook
        :return: NULL
        """
        sql = "DELETE FROM notebooks WHERE id = ?"
        # Execute delete
        self.db.execute(sql, [notebook_id])

    def get_all_notebooks(self):
        """
        Retrieve all notebooks
        :return: List of all notebooks in database
        """
        sql = "SELECT * FROM notebooks"
        return self.db.fetchall(sql)