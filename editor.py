import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

class Knowgent:
    def __init__(self, root):
        self.root = root
        self.text_area = tk.Text(root)
        self.text_area.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)

        self.file_path = None  # 当前打开的文件路径
        self.create_menu()
        self.create_file_browser()  # 创建文件浏览器

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Create New File", command=self.create_new_file, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Select Directory", command=self.select_directory, accelerator="Ctrl+D")
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # 编辑菜单
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+R")

        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menu_bar)

        # 绑定快捷键
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda event: self.save_file_as())
        self.root.bind('<Control-n>', lambda event: self.create_new_file())
        self.root.bind('<Control-d>', lambda event: self.select_directory())
        self.root.bind('<Control-q>', lambda event: self.root.quit())
        self.root.bind('<Control-x>', lambda event: self.cut_text())
        self.root.bind('<Control-c>', lambda event: self.copy_text())
        self.root.bind('<Control-v>', lambda event: self.paste_text())
        self.root.bind('<Control-a>', lambda event: self.select_all())
        self.root.bind('<Control-f>', lambda event: self.find_text())
        self.root.bind('<Control-r>', lambda event: self.replace_text())

    def create_file_browser(self):
        file_browser_frame = tk.Frame(self.root)
        file_browser_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.tree = ttk.Treeview(file_browser_frame)
        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.heading("#0", text="Directory Structure", anchor='w')

        self.tree.bind("<Double-1>", self.on_double_click)  # 双击打开文件
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)  # 右键菜单

        self.populate_tree(os.path.expanduser("~"))

    def populate_tree(self, path):
        """初始化或重新加载目录树"""
        self.tree.delete(*self.tree.get_children())
        root_node = self.tree.insert("", "end", text=path, open=True)
        self.process_directory(root_node, path)

    def process_directory(self, parent_node, path):
        """处理并加载目录内容"""
        try:
            self.tree.delete(*self.tree.get_children(parent_node))
            items = sorted([item for item in os.listdir(path) if not item.startswith('.')])
            for item in items:
                full_path = os.path.join(path, item)
                is_directory = os.path.isdir(full_path)

                node = self.tree.insert(parent_node, "end", text=item, open=False)
                if is_directory:
                    self.tree.insert(node, "end", text="Loading...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {e}")

    def on_double_click(self, event):
        """双击打开文件"""
        item = self.tree.selection()[0]
        file_name = self.tree.item(item, "text")
        full_path = self.get_full_path(item)

        if os.path.isfile(full_path):
            self.open_file(full_path)

    def get_full_path(self, item):
        """获取完整路径"""
        path_parts = []
        while item:
            path_parts.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return os.path.join(*path_parts)

    def open_file(self, file_path=None):
        """打开文件，并记录文件路径"""
        if not file_path:
            file_path = filedialog.askopenfilename()

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.file_path = file_path
                self.root.title(f"Simple Text Editor - {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """保存文件，使用当前文件路径"""
        if self.file_path:
            try:
                with open(self.file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Success", f"File saved successfully at {self.file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """另存为新文件"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.file_path = file_path
                self.root.title(f"Simple Text Editor - {file_path}")
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def create_new_file(self):
        """创建新文件"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a directory.")
            return

        full_path = self.get_full_path(selected_item[0])
        if os.path.isdir(full_path):
            file_name = filedialog.asksaveasfilename(initialdir=full_path, defaultextension=".txt")
            if file_name:
                try:
                    open(file_name, 'w').close()
                    self.process_directory(selected_item[0], full_path)
                    messagebox.showinfo("Success", "File created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create file: {e}")
        else:
            messagebox.showerror("Error", "Selected item is not a directory.")

    def select_directory(self):
        """选择新目录"""
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.populate_tree(selected_directory)

    def on_open_node(self, event):
        """展开子目录"""
        selected_item = self.tree.selection()[0]
        full_path = self.get_full_path(selected_item)
        self.tree.delete(*self.tree.get_children(selected_item))
        self.process_directory(selected_item, full_path)

    def show_context_menu(self, event):
        """显示右键菜单"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Rename", command=self.rename_file)
        context_menu.post(event.x_root, event.y_root)

    def rename_file(self):
        """重命名文件"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file or directory.")
            return

        old_name = self.tree.item(selected_item[0], "text")
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name:
            full_path = self.get_full_path(selected_item[0])
            new_full_path = os.path.join(os.path.dirname(full_path), new_name)

            try:
                os.rename(full_path, new_full_path)
                self.tree.item(selected_item[0], text=new_name)  # 更新树视图中的名称
                messagebox.showinfo("Success", "File renamed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file: {e}")

    # 编辑功能
    def cut_text(self):
        """剪切选中的文本"""
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        """复制选中的文本"""
        self.root.clipboard_clear()
        text = self.text_area.get("sel.first", "sel.last")
        self.root.clipboard_append(text)

    def paste_text(self):
        """粘贴文本"""
        text = self.root.clipboard_get()
        self.text_area.insert(tk.INSERT, text)

    def select_all(self):
        """全选文本"""
        self.text_area.tag_add("sel", "1.0", tk.END)

    def find_text(self):
        """查找文本"""
        find_word = simpledialog.askstring("Find", "Enter text to find:")
        if find_word:
            start = '1.0'
            while True:
                start = self.text_area.search(find_word, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(find_word)}c"
                self.text_area.tag_add("found", start, end)
                start = end

            self.text_area.tag_config("found", foreground="red")
    
    def replace_text(self):
        """替换文本"""
        replace_word = simpledialog.askstring("Replace", "Enter text to replace:")
        new_word = simpledialog.askstring("With", "Enter new text:")
        if replace_word and new_word:
            content = self.text_area.get("1.0", tk.END)
            updated_content = content.replace(replace_word, new_word)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", updated_content)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Knowgent v0.1.0")
    root.geometry("800x600")
    editor = Knowgent(root)
    root.mainloop()
