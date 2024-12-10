from pathlib import Path
from application.models.notebook_model import NotebookModel

class NotebookService:
    def __init__(self, db):
        """
        Initialize the NotebookService with a connection to the database
        :param db: connection to the database
        :raises ValueError: if the database connection is invalid
        """
        try:
            if db is None:
                raise ValueError("Databse connection cannot be None")
            self.notebook_model = NotebookModel(db)
        except  as e:
        
    def create_notebook(self, base_path, notebook_name, notebook_path, description):
        """
        Create a new notebook
        :param base_path: base path where notebooks are stored
        :param notebook_name: name of the new notebook
        :param notebook_path: path of the new notebook
        :param description: description of the new notebook
        :return: True if the notebook is created successfully, False otherwise
        """
        try:
            # Create the directory for the new notebook
            
