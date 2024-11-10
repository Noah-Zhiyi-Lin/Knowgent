import os
from tkinter import messagebox

class FileManager:
    def __init__(self):
        self.current_file_path = None

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.current_file_path = file_path
                return content
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            return None

    def save_file(self, content, file_path=None):
        save_path = file_path or self.current_file_path
        if not save_path:
            return False
            
        try:
            with open(save_path, 'w') as file:
                file.write(content)
            self.current_file_path = save_path
            messagebox.showinfo("Success", f"File saved successfully at {save_path}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False

    def create_file(self, file_path):
        try:
            open(file_path, 'w').close()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not create file: {e}")
            return False

    def rename_file(self, old_path, new_path):
        try:
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename file: {e}")
            return False

    def get_directory_contents(self, path):
        try:
            return sorted([item for item in os.listdir(path) if not item.startswith('.')])
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {e}")
            return []

    def is_directory(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)