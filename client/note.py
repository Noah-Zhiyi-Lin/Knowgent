from server.application.services.note_service import NoteService
from server.application.services.note_tag_service import NoteTagService

class Note:
    def __init__(self, db, title, notebook_name):
        self.note_service = NoteService(db)  # 初始化 NoteService
        self.note_tag_service = NoteTagService(db)  # 初始化 NoteTagService
        self.title = title  # 笔记标题
        self.notebook_name = notebook_name  # 笔记本名称

    def create(self):
        """创建笔记"""
        try:
            success = self.note_service.create_note(self.title, self.notebook_name)
            if success:
                print('Note created successfully')
        except Exception as e:
            print(f'Failed to create note: {e}')

    def get_content(self):
        """获取笔记内容"""
        try:
            content = self.note_service.get_note(self.title, self.notebook_name)
            return content
        except Exception as e:
            print(f'Failed to get note content: {e}')

    def update(self, new_title=None, new_notebook_name=None):
        """更新笔记"""
        try:
            success = self.note_service.update_note(
                title=self.title,
                notebook_name=self.notebook_name,
                new_title=new_title,
                new_notebook_name=new_notebook_name
            )
            if success:
                print('Note updated successfully')
        except Exception as e:
            print(f'Failed to update note: {e}')

    def delete(self):
        """删除笔记"""
        try:
            success = self.note_service.delete_note(self.title, self.notebook_name)
            if success:
                print('Note deleted successfully')
        except Exception as e:
            print(f'Failed to delete note: {e}')

    def add_tag(self, tag_name):
        """将标签添加到笔记"""
        try:
            success = self.note_tag_service.add_tag_to_note(self.title, self.notebook_name, tag_name)
            if success:
                print(f'Tag "{tag_name}" added to note "{self.title}" successfully')
        except Exception as e:
            print(f'Failed to add tag to note: {e}')

    def remove_tag(self, tag_name):
        """从笔记中移除标签"""
        try:
            success = self.note_tag_service.remove_tag_from_note(self.title, self.notebook_name, tag_name)
            if success:
                print(f'Tag "{tag_name}" removed from note "{self.title}" successfully')
        except Exception as e:
            print(f'Failed to remove tag from note: {e}')

    def get_tags(self):
        """获取与笔记关联的所有标签"""
        try:
            tags = self.note_tag_service.get_notes_for_tag(self.title, self.notebook_name)
            return tags
        except Exception as e:
            print(f'Failed to get tags for note: {e}')