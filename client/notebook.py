from server.application.services.notebook_service import NotebookService
from server.application.services.note_service import NoteService

class Notebook:
    def __init__(self, db, notebook_name, description=None):
        self.notebook_service = NotebookService(db)  # 初始化 NotebookService
        self.note_service = NoteService(db)  # 初始化 NoteService
        self.notebook_name = notebook_name  # 笔记本名称
        self.description = description  # 笔记本描述

    def create(self):
        """创建笔记本"""
        try:
            success = self.notebook_service.create_notebook(base_path="path/to/notebooks", 
                                                             notebook_name=self.notebook_name, 
                                                             description=self.description)
            if success:
                print('Notebook created successfully')
        except Exception as e:
            print(f'Failed to create notebook: {e}')

    def get(self):
        """获取笔记本信息"""
        try:
            notebook_info = self.notebook_service.get_notebook(self.notebook_name)
            return notebook_info
        except Exception as e:
            print(f'Failed to get notebook: {e}')

    def update(self, new_name=None, new_description=None):
        """更新笔记本信息"""
        try:
            success = self.notebook_service.update_notebook(self.notebook_name, 
                                                            base_path="path/to/notebooks", 
                                                            new_name=new_name, 
                                                            new_description=new_description)
            if success:
                print('Notebook updated successfully')
        except Exception as e:
            print(f'Failed to update notebook: {e}')

    def delete(self):
        """删除笔记本"""
        try:
            success = self.notebook_service.delete_notebook(self.notebook_name, 
                                                             base_path="path/to/notebooks")
            if success:
                print('Notebook deleted successfully')
        except Exception as e:
            print(f'Failed to delete notebook: {e}')

    def get_notes(self):
        """获取笔记本中的所有笔记"""
        try:
            notes = self.note_service.get_all_notes_in_notebook(self.notebook_name)
            return notes
        except Exception as e:
            print(f'Failed to get notes from notebook: {e}')