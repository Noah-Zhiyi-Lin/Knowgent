import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinterweb import HtmlFrame
from .menu_builder import MenuBuilder
from backend.file_manager import FileManager
from backend.text_processor import TextProcessor

class KnowgentGUI:
    def __init__(self, root):
        self.root = root
        self.file_manager = FileManager()
        self.text_processor = TextProcessor()
        self.markdown_mode = False  # 添加markdown模式标志
        
        self.setup_gui()
        self.menu_builder = MenuBuilder(self)
        
    def setup_gui(self):
        # 创建主面板
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 创建左侧文件浏览器框架
        self.file_browser_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.file_browser_frame)

        # 创建编辑器框架
        self.editor_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.editor_frame)

        # 创建工具栏
        self.toolbar = ttk.Frame(self.editor_frame)
        self.toolbar.pack(fill=tk.X)
        
        # 添加Markdown切换按钮
        self.markdown_button = ttk.Button(
            self.toolbar, 
            text="Enable Markdown Preview", 
            command=self.toggle_markdown_preview
        )
        self.markdown_button.pack(side=tk.LEFT, padx=5, pady=2)

        # 创建文本编辑区
        self.text_area = tk.Text(self.editor_frame)
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # 创建预览区（初始时不显示）
        self.preview_frame = ttk.Frame(self.paned_window)
        self.preview_area = HtmlFrame(self.preview_frame)
        self.preview_area.pack(fill=tk.BOTH, expand=True)

        # 绑定文本变化事件
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        
        # 创建文件浏览器
        self.create_file_browser()

    def create_file_browser(self):
        self.tree = ttk.Treeview(self.file_browser_frame)
        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.heading("#0", text="Directory Structure", anchor='w')

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.populate_tree(os.path.expanduser("~"))

    def toggle_markdown_preview(self):
        """切换Markdown预览模式"""
        self.markdown_mode = not self.markdown_mode
        
        if self.markdown_mode:
            # 启用预览模式
            self.markdown_button.configure(text="Disable Markdown Preview")
            self.paned_window.add(self.preview_frame)  # 添加预览窗口
            self.update_preview()  # 更新预览内容
        else:
            # 禁用预览模式
            self.markdown_button.configure(text="Enable Markdown Preview")
            self.paned_window.remove(self.preview_frame)  # 移除预览窗口

    def populate_tree(self, path):
        self.tree.delete(*self.tree.get_children())
        root_node = self.tree.insert("", "end", text=path, open=True)
        self.process_directory(root_node, path)

    def process_directory(self, parent_node, path):
        try:
            self.tree.delete(*self.tree.get_children(parent_node))
            items = self.file_manager.get_directory_contents(path)
            for item in items:
                full_path = os.path.join(path, item)
                is_directory = self.file_manager.is_directory(full_path)

                node = self.tree.insert(parent_node, "end", text=item, open=False)
                if is_directory:
                    self.tree.insert(node, "end", text="Loading...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {e}")

    def get_full_path(self, item):
        path_parts = []
        while item:
            path_parts.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return os.path.join(*path_parts)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        full_path = self.get_full_path(item)
        if self.file_manager.is_file(full_path):
            self.open_file(full_path)

    def on_text_modified(self, event=None):
        """当文本内容改变时触发"""
        if self.text_area.edit_modified():
            self.text_area.edit_modified(False)
            if self.markdown_mode:
                self.update_preview()

    def update_preview(self):
        """更新预览区域"""
        if not self.markdown_mode:
            return
            
        markdown_text = self.text_area.get("1.0", tk.END)
        html_content = self.text_processor.convert_markdown_to_html(markdown_text)
        styled_html = f"""
        <html>
            <head>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        padding: 20px; 
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                    }}
                    h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; }}
                    h2 {{ color: #34495e; border-bottom: 1px solid #eee; }}
                    h3 {{ color: #445566; }}
                    code {{ 
                        background-color: #f7f7f7; 
                        padding: 2px 5px; 
                        border-radius: 3px;
                        font-family: Consolas, monospace;
                    }}
                    pre {{ 
                        background-color: #f7f7f7; 
                        padding: 15px; 
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                    blockquote {{ 
                        border-left: 4px solid #ccc; 
                        margin: 0; 
                        padding: 5px 15px;
                        background-color: #f9f9f9;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 15px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f5f5f5;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
        self.preview_area.load_html(styled_html)

    def open_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Markdown Files", "*.md *.markdown"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*")
                ]
            )
        
        if file_path:
            content = self.file_manager.read_file(file_path)
            if content is not None:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, content)
                self.root.title(f"Knowgent - {file_path}")
                
                # 如果是markdown文件，自动启用markdown模式
                if file_path.lower().endswith(('.md', '.markdown')) and not self.markdown_mode:
                    self.toggle_markdown_preview()
                elif self.markdown_mode:
                    self.update_preview()

    def save_file(self):
        content = self.text_area.get(1.0, tk.END)
        if not self.file_manager.current_file_path:
            self.save_file_as()
        else:
            self.file_manager.save_file(content)

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[
                ("Markdown Files", "*.md *.markdown"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            content = self.text_area.get(1.0, tk.END)
            if self.file_manager.save_file(content, file_path):
                self.root.title(f"Knowgent - {file_path}")

    def create_new_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a directory.")
            return

        full_path = self.get_full_path(selected_item[0])
        if self.file_manager.is_directory(full_path):
            file_name = filedialog.asksaveasfilename(initialdir=full_path, defaultextension=".txt")
            if file_name:
                if self.file_manager.create_file(file_name):
                    self.process_directory(selected_item[0], full_path)
                    messagebox.showinfo("Success", "File created successfully!")
        else:
            messagebox.showerror("Error", "Selected item is not a directory.")

    def select_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.populate_tree(selected_directory)

    def on_open_node(self, event):
        selected_item = self.tree.selection()[0]
        full_path = self.get_full_path(selected_item)
        self.process_directory(selected_item, full_path)

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Rename", command=self.rename_file)
        context_menu.post(event.x_root, event.y_root)

    def rename_file(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file or directory.")
            return

        old_name = self.tree.item(selected_item[0], "text")
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name:
            full_path = self.get_full_path(selected_item[0])
            new_full_path = os.path.join(os.path.dirname(full_path), new_name)

            if self.file_manager.rename_file(full_path, new_full_path):
                self.tree.item(selected_item[0], text=new_name)
                messagebox.showinfo("Success", "File renamed successfully!")

    def cut_text(self):
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        self.root.clipboard_clear()
        try:
            text = self.text_area.get("sel.first", "sel.last")
            self.root.clipboard_append(text)
        except tk.TclError:
            pass  # 没有选中文本时不执���操作

    def paste_text(self):
        try:
            text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, text)
        except tk.TclError:
            pass  # 剪贴板为空时不执行操作

    def select_all(self):
        self.text_area.tag_add("sel", "1.0", tk.END)

    def find_text(self):
        find_word = simpledialog.askstring("Find", "Enter text to find:")
        if find_word:
            content = self.text_area.get("1.0", tk.END)
            positions = self.text_processor.find_all_occurrences(content, find_word)
            
            self.text_area.tag_remove("found", "1.0", tk.END)
            for start, end in positions:
                self.text_area.tag_add("found", f"1.0+{start}c", f"1.0+{end}c")
            self.text_area.tag_config("found", foreground="red")

    def replace_text(self):
        replace_word = simpledialog.askstring("Replace", "Enter text to replace:")
        new_word = simpledialog.askstring("With", "Enter new text:")
        if replace_word and new_word:
            content = self.text_area.get("1.0", tk.END)
            updated_content = self.text_processor.replace_all(content, replace_word, new_word)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", updated_content)