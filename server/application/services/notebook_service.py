from pathlib import Path
from server.application.models.notebook_model import NotebookModel
from server.application.exceptions import (
    ValidationError,
    DatabaseError,
    NotebookError,
    NotebookNotFoundError,
    DuplicateNotebookError,
    FileSystemError
)

class NotebookService:
    def __init__(self, db):
        """
        Initialize the NotebookService with a connection to the database
        :param db: connection to the database
        :rasises NotebookError: if service initialization fails
        """
        try:
            self.notebook_model = NotebookModel(db)
        except ValidationError as e:
            raise NotebookError(f"Failed to initialize NotebookService: {str(e)}")
        except Exception as e:
            raise NotebookError(f"Unexcepted error during NotebookService initialization: {str(e)}")
        
    def create_notebook(self, base_path, notebook_name, description):
        """
        Create a new notebook
        :param base_path: base path where notebooks are stored
        :param notebook_name: name of the new notebook
        :param description: description of the new notebook (optional)
        :raises NotebookError: if notebook creation fails
        :return: True if the notebook is created successfully, False otherwise
        """
        try:
            # Create the directory for the new notebook
            notebook_path = Path(base_path) / notebook_name
            try:
                notebook_path.mkdir(parents = True, exist_ok = True)
            except OSError as e:
                raise FileSystemError(f"Failed to create notebook directory: {str(e)}")
            # Create the notebook in the database
            self.notebook_model.create_notebook(
                notebook_name = notebook_name,
                notebook_path = str(notebook_path),
                description = description
            )
            return True
        except (ValidationError, DuplicateNotebookError, DatabaseError) as e:
            # If the directory already exists, remove it
            if notebook_path.exists():
                self._remove_dir(notebook_path)
            raise NotebookError(f"Failed to create notebook {notebook_name}: {str(e)}")
        except FileSystemError as e:
            raise NotebookError(f"Failed to create notebook {notebook_name}: {str(e)}")
        except Exception as e:
            if notebook_path and notebook_path.exists():
                self._remove_dir(notebook_path)
            raise NotebookError(f"Failed to create notebook {notebook_name}: {str(e)}")

    def get_notebook(self, notebook_name):
        """
        Get a notebook by its name
        :param notebook_name: name of the notebook
        :raises NotebookError: if retrieval fails
        :return: notebook details or None if not found
        """
        try:
            notebook_id = self.notebook_model.get_notebook_id(notebook_name)
            return self.notebook_model.get_notebook(notebook_id)
        except (ValidationError, NotebookNotFoundError, DatabaseError, Exception) as e:
            raise NotebookError(f"Failed to get notebook {notebook_name}: {str(e)}")
        
    def update_notebook(self, notebook_name, base_path, new_name = None, new_description = None):
        """
        Update a notebook's details
        :param notebook_name: current name of the notebook
        :param base_path: base path where notebooks are stored
        :param new_name: new name of the notebook
        :param new_description: new description of the notebook
        :raises NotebookError: if update fails
        :return: True if the notebook is updated successfully, False otherwise
        """
        try:
            notebook_id = self.notebook_model.get_notebook_id(notebook_name)
            # Change the path of the notebook if the new name is given
            new_path = None
            if new_name:
                if(new_name == notebook_name):
                    raise ValidationError("New notebook name must be different from the current notebook name")
                current_path = Path(base_path) / notebook_name
                new_path = Path(base_path) / new_name
                if current_path.exists():
                    current_path.rename(new_path)
            self.notebook_model.update_notebook(
                notebook_id = notebook_id,
                new_name = new_name,
                new_path = str(new_path) if new_path else None,
                new_description = new_description
            )
            return True
        except (ValidationError, 
                NotebookNotFoundError,
                DuplicateNotebookError,
                DatabaseError,
                Exception) as e:
            # Restore the original directory if update fails
            if new_path and new_path.exists():
                new_path.rename(current_path)
            raise NotebookError(f"Failed to update notebook {notebook_name}: {str(e)}")
        
    def delete_notebook(self, notebook_name, base_path):
        """
        Delete a notebook
        :param notebook_name: name of the notebook
        :param base_path: base path where notebooks are stored
        :raises NotebookError: if deletion fails
        :return: True if the notebook is deleted successfully, False otherwise
        """
        try:
            notebook_id = self.notebook_model.get_notebook_id(notebook_name)
            notebook_path = Path(base_path) / notebook_name
            # Delete the notebook from the database
            self.notebook_model.delete_notebook(notebook_id)
            # Delete the notebook directory
            if notebook_path.exists():
                self._remove_dir(notebook_path)
            return True
        except (ValidationError,
                NotebookNotFoundError,
                DatabaseError,
                FileSystemError,
                Exception) as e:
            raise NotebookError(f"Failed to delete notebook {notebook_name}: {str(e)}")
        
    def get_all_notebooks(self):
        """
        Get all notebooks from the database
        :raises NotebookError: if retrieval fails
        :return: list of all notebooks
        """
        try:
            return self.notebook_model.get_all_notebooks()
        except (DatabaseError, Exception) as e:
            raise NotebookError(f"Failed to get all notebooks: {str(e)}")

    def _remove_dir(self, path):
        """
        Remove a directory
        :param path: path of the directory
        :raises FileSystemError: if removal fails
        :return: None
        """
        try:
            if path.exists():
                for item in path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        self._remove_dir(item)
                path.rmdir()
        except Exception as e:
            raise FileSystemError(f"Failed to remove directory {path}: {str(e)}")