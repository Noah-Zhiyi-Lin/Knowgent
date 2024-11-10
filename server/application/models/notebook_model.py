from datetime import datetime

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

