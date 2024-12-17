from server.application.services.tag_service import TagService

class Tag:
    def __init__(self, db, tag_name):
        self.tag_service = TagService(db)  # 初始化 TagService
        self.tag_name = tag_name  # 标签名称

    def create(self):
        """创建标签"""
        try:
            success = self.tag_service.create_tag(self.tag_name)
            if success:
                print('Tag created successfully')
        except Exception as e:
            print(f'Failed to create tag: {e}')

    def get(self):
        """获取标签信息"""
        try:
            tag_info = self.tag_service.get_tag(self.tag_name)
            return tag_info
        except Exception as e:
            print(f'Failed to get tag: {e}')

    def update(self, new_name):
        """更新标签名称"""
        try:
            success = self.tag_service.update_tag(self.tag_name, new_name)
            if success:
                print('Tag updated successfully')
        except Exception as e:
            print(f'Failed to update tag: {e}')

    def delete(self):
        """删除标签"""
        try:
            success = self.tag_service.delete_tag(self.tag_name)
            if success:
                print('Tag deleted successfully')
        except Exception as e:
            print(f'Failed to delete tag: {e}')

    def get_all_tags(self):
        """获取所有标签"""
        try:
            all_tags = self.tag_service.get_all_tags()
            return all_tags
        except Exception as e:
            print(f'Failed to get all tags: {e}')
