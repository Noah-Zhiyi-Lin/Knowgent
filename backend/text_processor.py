import markdown

class TextProcessor:
    def __init__(self):
        self.md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite'])

    def convert_markdown_to_html(self, text):
        """将Markdown文本转换为HTML"""
        try:
            return self.md.convert(text)
        except Exception as e:
            return f"<p>Error converting markdown: {str(e)}</p>"
        finally:
            self.md.reset()  # 重置转换器状态

    @staticmethod
    def find_all_occurrences(text, search_term):
        positions = []
        start = 0
        while True:
            start = text.find(search_term, start)
            if start == -1:
                break
            end = start + len(search_term)
            positions.append((start, end))
            start = end
        return positions

    @staticmethod
    def replace_all(text, old_text, new_text):
        return text.replace(old_text, new_text)