class NotebookModel:
    def __init__(self, db):
        # Database connection
        self.db = db

    def create_notebook(self, notebook_name, notebook_path, description):
        """
        Create a new notebook
        :param notebook_name: name of the new notebook
        :param notebook_path: path of the new notebook
        :param description: description of the new notebook
        :return: None
        """
        sql = """
        INSERT INTO notebooks (notebook_name, notebook_path, description)
        VALUES (?, ?, ?)
        """
        params = [notebook_name, notebook_path, description]
        self.db.execute(sql, params)

    def get_notebook_by_name(self, notebook_name):
        """
        Retrieve a notebook's details by its name
        :param notebook_name: name of the notebook
        :return: row of the notebook in database
        """
        sql = "SELECT * FROM notebooks WHERE notebook_name = ?"
        return self.db.fetchone(sql, [notebook_name])

    def get_id_by_name(self, notebook_name):
        """
        Retrieve a notebook's ID by its name
        :param notebook_name: name of the notebook
        :return: ID of the notebook in database
        """
        sql = "SELECT id FROM notebooks WHERE notebook_name = ?"
        result = self.db.fetchone(sql, [notebook_name])
        return result["id"] if result else None

    def update_notebook_by_name(self, notebook_name, new_name=None, new_path=None, new_description=None):
        """
        Update a notebook's details by its current name
        :param notebook_name: current name of the notebook
        :param new_name: new name of the notebook
        :param new_path: new path of the notebook
        :param new_description: new description of the notebook
        :return: None
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
        sql += " updated_at = CURRENT_TIMESTAMP WHERE notebook_name = ?"
        params.append(notebook_name)
        # Execute update
        self.db.execute(sql, params)

    def delete_notebook_by_name(self, notebook_name):
        """
        Delete a notebook by its name
        :param notebook_name: name of the notebook
        :return: None
        """
        sql = "DELETE FROM notebooks WHERE notebook_name = ?"
        # Execute delete
        self.db.execute(sql, [notebook_name])

    def get_all_notebooks(self):
        """
        Retrieve all notebooks
        :return: rows of all notebooks in database
        """
        sql = "SELECT * FROM notebooks"
        return self.db.fetchall(sql)