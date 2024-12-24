from pathlib import Path
from server.application.models.note_model import NoteModel
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
            self.__note_model = NoteModel(db)
            self.__base_path = self.__note_model.db.get_base_path()
            self.__notebook_service = None
        except ValidationError as e:
            raise NoteError(f"Failed to initialize NoteService: {str(e)}")
        except Exception as e:
            raise NoteError(f"Unexpected error during NoteService initialization: {str(e)}")
    
    # Inject dependency
    @property
    def notebook_service(self):
        if not self.__notebook_service:
            raise NotebookError("NotebookService not set")
        return self.__notebook_service
    
    @notebook_service.setter
    def notebook_service(self, service):
        self.__notebook_service = service
    
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
            # Create note file path
            file_path = Path(f"{self.__base_path}/{notebook_name}/{title}.md")
            # Try to create the note
            try:
                file_path.touch(exist_ok = False)
            except FileExistsError:
                raise FileSystemError(f"Note file already exists: {file_path}")
            except Exception as e:
                raise FileSystemError(f"Failed to create note file: {str(e)}")
            # Try to create the note in the database
            try:
                self.__note_model.create_note(title, notebook_id)
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
            except NotebookError as e:
                raise e
            notebook_id = notebook["id"]
            note_id = self.__note_model.get_note_id(title, notebook_id)
            return self.__note_model.get_note(note_id)
        except (ValidationError, NoteNotFoundError, NotebookError, DatabaseError) as e:
            raise NoteError(f"Failed to get note {title} in notebook {notebook_name}: {str(e)}")

    # def get_note_file_path(self, title, notebook_name):
    #     """
    #     获取笔记的文件路径
    #     :param title: 笔记的标题
    #     :param notebook_name: 笔记本的名称
    #     :raises NoteError: 如果获取文件路径失败
    #     :return: 笔记的文件路径
    #     """
    #     try:
    #         # 获取笔记本的 ID
    #         notebook = self.notebook_service.get_notebook(notebook_name)
    #         notebook_id = notebook["id"]

    #         # 获取笔记的 ID
    #         note_id = self.__note_model.get_note_id(title, notebook_id)

    #         # 获取笔记的详细信息
    #         note_dict = self.__note_model.get_note(note_id)

    #         # 返回笔记的文件路径
    #         return note_dict["file_path"]
    #     except (NotebookError, NoteNotFoundError, DatabaseError, Exception) as e:
    #         raise NoteError(f"Failed to get file path for note {title} in notebook {notebook_name}: {str(e)}")
      
    def get_note_file_path(self, title, notebook_name):
        """
        Get the path of note
        :param: title: title of the note
        :param: notebook_name: name of the notebook which the note belongs to
        :raises: NoteError: if failed to get the path
        :return: the path of the note
        """
        try:
            # Check whether the note exists
            try:
                self.get_note(title, notebook_name)
            except NoteError as e:
                raise e
            return f"{self.__base_path}/{notebook_name}/{title}.md"
        except (NoteError, Exception) as e:
            raise NoteError(f"Fail to get note file path: {str(e)}")
    
    # def get_note_content(self, title, notebook_name):
    #     """
    #     Get the content of a note
    #     :param title: title of the note
    #     :param notebook_name: name of the notebook which the note belongs to
    #     :raises NoteError: if retrieval fails
    #     :return: content of the note
    #     """
    #     try:
    #         # Try to get the path of the note file
    #         try:
    #             note_dict = self.get_note(title, notebook_name)
    #         except NoteError as e:
    #             raise e
    #         file_path = note_dict["file_path"]

    #         # Check whether the file exists
    #         if not Path(file_path).exists():
    #             raise FileSystemError(
    #                 f"File of note {title} in notebook {notebook_name} does not exist: {file_path}"
    #             )

    #         # Try to read the note file
    #         try:
    #             with open(file_path, "r", encoding="utf-8") as file:
    #                 return file.read()
    #         except IOError as e:
    #             raise FileSystemError(
    #                 f"Failed to read the file of note {title} in notebook {notebook_name}: {str(e)}"
    #             )
    #     except (NoteError, FileSystemError, Exception) as e:
    #         raise NoteError(
    #             f"Failed to get the content of note {title} in notebook {notebook_name}: {str(e)}"
    #         )
    def get_note_content(self, title, notebook_name):
        """
        获取笔记的内容
        :param title: 笔记的标题
        :param notebook_name: 笔记本的名称
        :raises NoteError: 如果获取内容失败
        :return: 笔记的内容
        """
        try:
            # Try to get the path of the note file
            file_path = self.get_note_file_path(title, notebook_name)

            # Check whether the file exists
            if not Path(file_path).exists():
                raise FileSystemError(f"File of note {title} in notebook {notebook_name} does not exist: {file_path}")

            # Try to read the note file
            # with open(file_path, "r", encoding="utf-8") as file:
            try: 
                with open(file_path, "r") as file:
                    content = file.read()
            except:
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                except Exception as e:
                    raise e

            if not content:
                return ""

            return content
        except (NoteError, FileSystemError, Exception) as e:
            raise NoteError(f"Failed to get the content of note {title} in notebook {notebook_name}: {str(e)}")
    
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
            current_file_path = None
            # Try to get current file path
            try:
                current_file_path = Path(self.get_note_file_path(title, notebook_name))
            except NoteError as e:
                raise e
            new_file_path = None
            new_notebook_id = None
            # Handle notebook transfer
            if new_notebook_name:
                # Check whether new notebook exists
                try:
                    new_notebook = self.notebook_service.get_notebook(new_notebook_name)
                except NotebookError as e:
                    raise e
                new_notebook_id = new_notebook["id"]
                if new_title and not new_notebook_name: # Only rename the note
                    new_file_path = Path(f"{self.__base_path}/{notebook_name}/{new_title}.md")
                elif not new_title and new_notebook_name: # Transfer to new notebook with same title
                    new_file_path = Path(f"{self.__base_path}/{new_notebook_name}/{title}.md")
                else: # Transfer to new notebook with new title
                    new_file_path = Path(f"{self.__base_path}/{new_notebook_name}/{new_title}.md")
            # Handle title change
            elif new_title:
                new_file_path = current_file_path.parent / f"{new_title}.md"
            # Update note in the database
            try:
                self.__note_model.update_note(
                    note_id = note_id,
                    new_title = new_title if new_title else None,
                    new_notebook_id = new_notebook_id if new_notebook_id else None
                )
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
                return True
            except (
                ValidationError,
                NotebookNotFoundError,
                DuplicateNoteError,
                DatabaseError,
                FileSystemError,
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
            # Try to get note file path
            file_path = None
            try:
                file_path = Path(self.get_note_file_path(title, notebook_name))
            except NoteError as e:
                raise e
            # Delete note in database
            self.__note_model.delete_note(note_id)
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
    #         return self.__note_model.get_all_notes_in_notebook(notebook_id)
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
            return self.__note_model.get_all_notes()
        except (DatabaseError, Exception) as e:
            raise NoteError(f"Failed to get all notes: {str(e)}")

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
            return self.__note_model.get_all_notes_in_notebook(notebook_id)
        except (
            NotebookError,
            ValidationError,
            NotebookNotFoundError,
            DatabaseError,
            Exception
        ) as e:
            raise NoteError(f"Failed to get all notes in notebook {notebook_name}: {str(e)}")