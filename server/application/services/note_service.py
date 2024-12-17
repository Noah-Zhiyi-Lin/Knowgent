from pathlib import Path
from server.application.models.note_model import NoteModel
from server.application.services.notebook_service import NotebookService
from server.application.exceptions import (
    ValidationError,
    DatabaseError,
    NotebookError,
    NoteError,
    NoteNotFoundError,
    NotebookNotFoundError,
    DuplicateNoteError,
    FileSystemError
)

class NoteService:
    def __init__(self, db):
        """
        Initialize the NoteService with a connection to the database
        :param db: connection to the database
        :raises NoteError: if service initialization fails
        """
        try:
            self.note_model = NoteModel(db)
            self.notebook_service = NotebookService(db)
        except (ValidationError, NotebookError) as e:
            raise NoteError(f"Failed to initialize NoteService: {str(e)}")
        except Exception as e:
            raise NoteError(f"Unexpected error during NoteService initialization: {str(e)}")
        
    def create_note(self, title, notebook_name):
        """
        Create a new note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :raises NoteError: if note creation fails
        :return: True if the note is created successfully, False otherwise
        """
        try:
            # Try to get the notebook
            try:
                notebook = self.notebook_service.get_notebook(notebook_name)
            except NotebookError as e:
                raise e
            notebook_id = notebook["id"]
            notebook_path = notebook["notebook_path"]
            # Create note file path
            file_path = Path(notebook_path) / f"{title}.md"
            # Try to create the note
            try:
                file_path.touch(exist_ok = False)
            except FileExistsError:
                raise FileSystemError(f"Note file already exists: {file_path}")
            except Exception as e:
                raise FileSystemError(f"Failed to create note file: {str(e)}")
            # Try to create the note in the database
            try:
                self.note_model.create_note(title, str(file_path), notebook_id)
                return True
            except (
                ValidationError,
                NotebookNotFoundError,
                DuplicateNoteError,
                DatabaseError,
                Exception
            ) as e:
                # If database operation fails, delete the note file
                if file_path.exists():
                    file_path.unlink()
                raise e
        except (
            NotebookError,
            ValidationError,
            NotebookNotFoundError,
            DuplicateNoteError,
            DatabaseError,
            FileSystemError,
            Exception
        ) as e:
            raise NoteError(f"Failed to create note {title} in notebook {notebook_name}: {str(e)}")
    
    # def get_note(self, title, notebook_name):
    #     """
    #     Get a note by its title
    #     :param: title: title of the note
    #     :param: notebook_name: name of the notebook which the note belongs to
    #     :raises NoteError: if retrieval fails
    #     :return: note details or None if not found
    #     """
    #     try:
    #         # Try to get notebook_id
    #         try:
    #             notebook = self.notebook_service.get_notebook(notebook_name)
    #         except NotebookError as e:
    #             raise e
    #         notebook_id = notebook["id"]
    #         note_id = self.note_model.get_note_id(title, notebook_id)
    #         return self.note_model.get_note(note_id)
    #     except (ValidationError, NoteNotFoundError, NotebookError, DatabaseError) as e:
    #         raise NoteError(f"Failed to get note {title} in notebook {notebook_name}: {str(e)}")
    
    def get_note_content(self, title, notebook_name):
        """
        Get the content of a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :raises NoteError: if retrieval fails
        :return: content of the note
        """
        try:
            # Try to get the path of the note file
            try:
                note = self.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            file_path = note["file_path"]
            # Check whether the file exists
            if not Path(file_path).exists():
                raise FileSystemError(
                    f"File of note {title} in notebook {notebook_name} does not exist: {file_path}"
                )
            # Try to read the note file
            try:
                with open(file_path, "r") as file:
                    return file.read()
            except IOError as e:
                raise FileSystemError(
                    f"Failed to read the file of note {title} in notebook {notebook_name}: {str(e)}"
                )
        except (NoteError, FileSystemError, Exception) as e:
            raise NoteError(
                f"Failed to get the content of note {title} in notebook {notebook_name}: {str(e)}"
            )
    
    def update_note(self, title, notebook_name, new_title = None, new_notebook_name = None):
        """
        Update a note's details
        :param title: current title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :param new_title: new title of the note
        :param new_notebook_name: the name of the new notebook which the note will belong to
        :raises NoteError: if update fails
        :return: True if update is successful, False otherwise
        """
        try:
            # Check current note status
            try:
                note = self.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            current_file_path = Path(note['file_path'])
            new_file_path = None
            # Handle notebook transfer
            if new_notebook_name:
                # Try to get the new notebook
                try:
                    new_notebook = self.notebook_service.get_notebook(new_notebook_name)
                except NotebookError as e:
                    raise e
                new_notebook_id = new_notebook["id"]
                new_notebook_path = new_notebook["notebook_path"]
                if new_title:
                    new_file_path = Path(new_notebook_path) / f"{new_title}.md"
                else:
                    new_file_path = Path(new_notebook_path) / f"{title}.md"
            # Handle title change
            elif new_title:
                new_file_path = current_file_path.parent / f"{new_title}.md"
            # Move note file if file path is changed
            if new_file_path:
                # Check whether the target file exists
                if new_file_path.exists():
                    raise FileSystemError(f"Note file already exists: {new_file_path}")
                # Try to move the note file
                try:
                    current_file_path.rename(new_file_path)
                except Exception as e:
                    raise FileSystemError(f"Failed to move note file: {str(e)}")
            # Update note in the database
            try:
                self.note_model.update_note(
                    note_id = note_id,
                    new_title = new_title if new_title else None,
                    new_path = new_file_path if new_file_path else None,
                    new_notebook_id = new_notebook_id if new_notebook_id else None
                )
                return True
            except (
                ValidationError,
                NotebookNotFoundError,
                DuplicateNoteError,
                DatabaseError,
                Exception
            ) as e:
                raise e
        except (
            NoteError,
            NotebookError,
            FileSystemError,
            ValidationError,
            NotebookNotFoundError,
            DuplicateNoteError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteError(f"Failed to update note {title} in notebook {notebook_name}: {str(e)}")

    def delete_note(self, title, notebook_name):
        """
        Delete a note
        :param title: title of the note
        :param notebook_name: name of the notebook which the note belongs to
        :raises NoteError: if deletion fails
        :return: True if the note is deleted successfully, False otherwise
        """
        try:
            # Try to get the note
            try:
                note = self.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            note_id = note["id"]
            file_path = Path(note["file_path"])
            # Delete note in database
            self.note_model.delete_note(note_id)
            # Delete note file
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    raise FileSystemError
            return True
        except (
            NoteError,
            ValidationError,
            NoteNotFoundError,
            DatabaseError,
            FileSystemError,
            Exception
        ) as e:
            raise NoteError(f"Failed to delete note {title} in notebook {notebook_name}: {str(e)}")
    
    # def get_all_notes_in_notebook(self, notebook_name):
    #     """
    #     Get all notes in a notebook
    #     :param: notebook_name: name of the notebook
    #     :raises: NoteError: if retrieval fails
    #     :return: all notes in the notebook
    #     """
    #     try:
    #         # Try to get notebook id
    #         try:
    #             notebook = self.notebook_service.get_notebook(notebook_name)
    #         except NotebookError as e:
    #             raise e
    #         notebook_id = notebook["id"]
    #         # Get all notes in the notebook
    #         return self.note_model.get_all_notes_in_notebook(notebook_id)
    #     except (
    #         NotebookError,
    #         ValidationError,
    #         NotebookNotFoundError,
    #         DatabaseError,
    #         Exception
    #     ) as e:
    #         raise NoteError(f"Failed to get all notes in notebook {notebook_name}: {str(e)}")
    
    def get_all_notes(self):
        """
        Get all notes
        :raises NoteError: if retrieval fails
        :return: all notes in the database
        """
        try:
            return self.note_model.get_all_notes()
        except (DatabaseError, Exception) as e:
            raise NoteError(f"Failed to get all notes: {str(e)}")
        

    def get_note(self, title, notebook_name):
        """
        Get a note by its title
        :param: title: title of the note
        :param: notebook_name: name of the notebook which the note belongs to
        :raises NoteError: if retrieval fails
        :return: note details or None if not found
        """
        try:
            # Try to get notebook_id
            try:
                notebook = self.notebook_service.get_notebook(notebook_name)
                print(notebook)
            except NotebookError as e:
                raise e
            notebook_id = notebook["id"]
            note_id = self.note_model.get_note_id(title, notebook_id)
            note_tuple = self.note_model.get_note(note_id)

            # 将元组转换为字典
            note_dict = {
                'id': note_tuple[0],
                'title': note_tuple[1],
                'file_path': note_tuple[2],
                'notebook_id': note_tuple[3],
                'created_at': note_tuple[4],
                'updated_at': note_tuple[5]
            }

            return note_dict
        except (ValidationError, NoteNotFoundError, NotebookError, DatabaseError) as e:
            raise NoteError(f"Failed to get note {title} in notebook {notebook_name}: {str(e)}")

    def get_all_notes_in_notebook(self, notebook_name):
        """
        Get all notes in a notebook
        :param: notebook_name: name of the notebook
        :raises: NoteError: if retrieval fails
        :return: all notes in the notebook
        """
        try:
            # Try to get notebook id
            try:
                notebook = self.notebook_service.get_notebook(notebook_name)
            except NotebookError as e:
                raise e
            notebook_id = notebook["id"]
            notes_tuples = self.note_model.get_all_notes_in_notebook(notebook_id)

            # 将元组列表转换为字典列表
            notes_dicts = []
            for note_tuple in notes_tuples:
                note_dict = {
                    'id': note_tuple[0],
                    'title': note_tuple[1],
                    'file_path': note_tuple[2],
                    'notebook_id': note_tuple[3],
                    'created_at': note_tuple[4],
                    'updated_at': note_tuple[5]
                }
                notes_dicts.append(note_dict)

            return notes_dicts
        except (
            NotebookError,
            ValidationError,
            NotebookNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteError(f"Failed to get all notes in notebook {notebook_name}: {str(e)}")