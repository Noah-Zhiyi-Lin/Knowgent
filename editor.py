import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class SimpleTextEditor:
    def __init__(self, root):
        self.root = root
        self.text_area = tk.Text(root)
        self.text_area.pack(fill=tk.BOTH, expand=1, side=tk.RIGHT)

        self.file_path = None  # 当前打开的文件路径
        self.create_menu()
        self.create_file_browser()  # 创建文件浏览器

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)

        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_command(label="Create New File", command=self.create_new_file)
        file_menu.add_separator()
        file_menu.add_command(label="Select Directory", command=self.select_directory)
        file_menu.add_command(label="Exit", command=self.root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def create_file_browser(self):
        file_browser_frame = tk.Frame(self.root)
        file_browser_frame.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.tree = ttk.Treeview(file_browser_frame)
        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.heading("#0", text="Directory Structure", anchor='w')

        self.tree.bind("<Double-1>", self.on_double_click)  # 双击打开文件
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)

        self.populate_tree(os.path.expanduser("~"))

    def populate_tree(self, path):
        """初始化或重新加载目录树"""
        self.tree.delete(*self.tree.get_children())
        root_node = self.tree.insert("", "end", text=path, open=True)
        self.process_directory(root_node, path)

    def process_directory(self, parent_node, path):
        """处理并加载目录内容"""
        try:
            # 清空当前节点的子节点，防止重复加载
            self.tree.delete(*self.tree.get_children(parent_node))
            
            # 排序并过滤掉隐藏文件
            items = sorted([item for item in os.listdir(path) if not item.startswith('.')])
            
            for item in items:
                full_path = os.path.join(path, item)
                is_directory = os.path.isdir(full_path)

                node = self.tree.insert(parent_node, "end", text=item, open=False)
                if is_directory:
                    self.tree.insert(node, "end", text="Loading...")  # 为目录节点加载提示符
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {e}")

    def on_double_click(self, event):
        """双击打开文件"""
        item = self.tree.selection()[0]
        file_name = self.tree.item(item, "text")
        full_path = self.get_full_path(item)

        if os.path.isfile(full_path):
            self.open_file(full_path)  # 通过文件浏览器打开文件

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
                self.file_path = file_path  # 记录打开的文件路径
                self.root.title(f"Simple Text Editor - {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def save_file(self):
        """保存文件，使用当前文件路径"""
        if self.file_path:  # 如果路径已经存在，直接保存
            try:
                with open(self.file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                messagebox.showinfo("Success", f"File saved successfully at {self.file_path}")
                print(f"File saved successfully at {self.file_path}")  # 控制台输出保存成功消息
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_file_as()  # 如果文件路径不存在，调用另存为

    def save_file_as(self):
        """另存为新文件"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                self.file_path = file_path  # 更新文件路径
                self.root.title(f"Simple Text Editor - {file_path}")
                messagebox.showinfo("Success", "File saved successfully!")
                print(f"File saved successfully at {file_path}")  # 控制台输出保存成功消息
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
                    open(file_name, 'w').close()  # 创建新文件
                    self.process_directory(selected_item[0], full_path)  # 刷新当前目录
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
        # 清空当前节点的子节点，以防重复加载
        self.tree.delete(*self.tree.get_children(selected_item))
        self.process_directory(selected_item, full_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simple Text Editor")
    root.geometry("800x600")
    editor = SimpleTextEditor(root)
    root.mainloop()

