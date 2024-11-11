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
        self.markdown_mode = False
        
        # 更新主题配色
        self.themes = {
            'Light': {
                'bg': '#FFFFFF',
                'fg': '#2C3E50',
                'selected_bg': '#3498DB',
                'hover_bg': '#E0E0E0',
                'editor_bg': '#FFFFFF',
                'editor_fg': '#2C3E50',
                'preview_bg': '#FFFFFF',
                'preview_fg': '#2C3E50',
                'window_bg': '#F0F0F0',  # 窗口背景色
                'menu_bg': '#F5F5F5',    # 菜单背景色
                'menu_fg': '#2C3E50',    # 菜单文字颜色
            },
            'Dark': {
                'bg': '#1E1E1E',
                'fg': '#D4D4D4',
                'selected_bg': '#264F78',
                'hover_bg': '#2D2D2D',
                'editor_bg': '#1E1E1E',
                'editor_fg': '#D4D4D4',
                'preview_bg': '#1E1E1E',
                'preview_fg': '#D4D4D4',
                'window_bg': '#1E1E1E',  # 窗口背景色
                'menu_bg': '#333333',    # 深色菜单背景色
                'menu_fg': '#D4D4D4',    # 深色菜单文字颜色
            }
        }
        self.current_theme = 'Light'
        
        # 初始化样式
        self.style = ttk.Style()
        self.setup_initial_styles()
        
        self.setup_gui()
        self.menu_builder = MenuBuilder(self)
        
        # 在所有组件创建完成后应用完整样式
        self.apply_theme_styles()

    def setup_initial_styles(self):
        """设置初始样式（在创建组件之前）"""
        try:
            self.style.theme_use('clam')
        except:
            pass

        theme = self.themes[self.current_theme]
        
        # 设置根窗口背景色和边框色
        self.root.configure(bg=theme['window_bg'])
        if self.current_theme == 'Dark':
            # 在Windows系统上设置深色标题栏
            try:
                from ctypes import windll, byref, sizeof, c_int
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                windll.dwmapi.DwmSetWindowAttribute(
                    windll.user32.GetParent(self.root.winfo_id()),
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    byref(c_int(1)),
                    sizeof(c_int)
                )
            except:
                pass
        
        # 定义颜色
        bg_color = theme['bg']
        fg_color = theme['fg']
        selected_bg = theme['selected_bg']
        hover_bg = theme['hover_bg']
        
        # 自定义Frame样式
        self.style.configure('Custom.TFrame', background=bg_color)
        
        # 自定义PanedWindow样式
        self.style.configure('Custom.TPanedwindow', 
            background=bg_color,
            sashwidth=4,  # 分隔条宽度
            sashpad=0,    # 分隔条内边距
            sashrelief=tk.FLAT  # 分隔条样式
        )
        
        # 自定义Button样式
        self.style.configure('Preview.TButton',
            padding=(10, 5),
            background=bg_color,
            foreground=fg_color,
            borderwidth=1,
            relief=tk.FLAT,
            font=('Arial', 9)
        )
        
        # 自定义Treeview样式
        self.style.configure('Treeview',
            background=bg_color,
            foreground=fg_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=('Arial', 10)
        )
        self.style.configure('Treeview.Heading',
            background=bg_color,
            foreground=fg_color,
            relief=tk.FLAT,
            font=('Arial', 10, 'bold')
        )
        
        self.style.map('Treeview',
            background=[('selected', selected_bg)],
            foreground=[('selected', '#FFFFFF')]
        )

        # 配置 Treeview.Heading 的鼠标悬停效果
        self.style.map('Treeview.Heading',
            background=[
                ('active', hover_bg),
                ('pressed', hover_bg)
            ],
            foreground=[
                ('active', fg_color),
                ('pressed', fg_color)
            ]
        )

        # 配置 Preview.TButton 的鼠标悬停效果
        self.style.map('Preview.TButton',
            background=[
                ('active', hover_bg),
                ('pressed', hover_bg)
            ],
            foreground=[
                ('active', fg_color),
                ('pressed', fg_color)
            ]
        )

        # 自定义滚动条样式
        self.style.configure('Custom.Vertical.TScrollbar',
            background=bg_color,
            arrowcolor=fg_color,
            bordercolor=bg_color,
            troughcolor=bg_color,
            relief=tk.FLAT,
            width=12  # 设置滚动条宽度
        )
        
        # 配置滚动条贴图
        self.style.map('Custom.Vertical.TScrollbar',
            background=[
                ('pressed', hover_bg),
                ('active', hover_bg),
                ('!active', bg_color)
            ],
            arrowcolor=[
                ('pressed', fg_color),
                ('active', fg_color),
                ('!active', fg_color)
            ]
        )

    def apply_theme_styles(self):
        """应用主题样式（在创建组件之后）"""
        theme = self.themes[self.current_theme]
        
        # 更新文本编辑器样式
        self.text_area.configure(
            bg=theme['editor_bg'],
            fg=theme['editor_fg'],
            insertbackground=theme['editor_fg'],
            selectbackground=theme['selected_bg'],
            selectforeground='#FFFFFF'
        )
        
        # 更新所有Frame的背景色
        for widget in [self.file_browser_frame, self.editor_frame, 
                      self.editor_top_frame, self.spacer]:
            widget.configure(style='Custom.TFrame')
            
        # 更新预览框架背景色
        if hasattr(self, 'preview_frame'):
            self.preview_frame.configure(style='Custom.TFrame')

    def change_theme(self, theme_name):
        """切换主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            theme = self.themes[theme_name]
            
            # 更新根窗口背景色
            self.root.configure(bg=theme['window_bg'])
            
            # 立即更新菜单栏颜色
            self.menu_builder.update_menu_colors(theme['menu_bg'], theme['menu_fg'])
            
            # 强制更新显示
            self.root.update_idletasks()
            
            self.setup_initial_styles()
            self.apply_theme_styles()
            if self.markdown_mode:
                self.update_preview()

    def setup_gui(self):
        # 创建主面板
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL, style='Custom.TPanedwindow')
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 创建左侧文件浏览器框架
        self.file_browser_frame = ttk.Frame(self.paned_window, style='Custom.TFrame')
        self.paned_window.add(self.file_browser_frame, weight=1)

        # 创建编辑器框架
        self.editor_frame = ttk.Frame(self.paned_window, style='Custom.TFrame')
        self.paned_window.add(self.editor_frame, weight=3)

        # 创建编辑器顶部框架
        self.editor_top_frame = ttk.Frame(self.editor_frame, style='Custom.TFrame')
        self.editor_top_frame.pack(fill=tk.X, padx=5, pady=5)

        # 创建一个空的填充框架
        self.spacer = ttk.Frame(self.editor_top_frame, style='Custom.TFrame')
        self.spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 添加Markdown预览按钮
        self.markdown_button = ttk.Button(
            self.editor_top_frame, 
            text="Preview",
            width=8,
            style='Preview.TButton',
            command=self.toggle_markdown_preview
        )
        self.markdown_button.pack(side=tk.RIGHT, padx=5, pady=2)

        # 创建文本编辑区和其滚动条
        editor_container = ttk.Frame(self.editor_frame, style='Custom.TFrame')
        editor_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 创建文本编辑区的滚动条
        editor_scrollbar = ttk.Scrollbar(
            editor_container,
            orient="vertical",
            style='Custom.Vertical.TScrollbar'
        )
        editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建文本编辑区
        self.text_area = tk.Text(
            editor_container,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            spacing1=2,
            spacing2=2,
            spacing3=2,
            font=('Consolas', 11),
            relief=tk.FLAT,
            borderwidth=0,
            yscrollcommand=editor_scrollbar.set
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        editor_scrollbar.config(command=self.text_area.yview)

        # 创建预览区
        self.preview_frame = ttk.Frame(self.paned_window, style='Custom.TFrame')
        self.preview_area = HtmlFrame(self.preview_frame)
        self.preview_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 绑定事件
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        
        # 创建文件浏览器
        self.create_file_browser()

    def create_file_browser(self):
        # 创建一个Frame来包含Treeview和滚动条
        browser_container = ttk.Frame(self.file_browser_frame, style='Custom.TFrame')
        browser_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 创建滚动条（使用自定义样式）
        scrollbar = ttk.Scrollbar(
            browser_container,
            orient="vertical",
            style='Custom.Vertical.TScrollbar'
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建Treeview
        self.tree = ttk.Treeview(
            browser_container,
            style='Treeview',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 配置滚动条
        scrollbar.config(command=self.tree.yview)

        # 设置标题
        self.tree.heading('#0', text="Directory Structure", anchor='w')

        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 初始化目录
        self.populate_tree(os.path.expanduser("~"))

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

    def toggle_markdown_preview(self):
        """切换Markdown预览模式"""
        self.markdown_mode = not self.markdown_mode
        
        if self.markdown_mode:
            # 启用预览模式
            self.markdown_button.configure(text="Hide")
            self.paned_window.add(self.preview_frame)  # 添加预览窗口
            self.update_preview()  # 更新预览内容
        else:
            # 禁用预览模式
            self.markdown_button.configure(text="Preview")
            self.paned_window.remove(self.preview_frame)  # 移除预览窗口

    def update_preview(self):
        """更新预览区域"""
        if not self.markdown_mode:
            return
            
        markdown_text = self.text_area.get("1.0", tk.END)
        html_content = self.text_processor.convert_markdown_to_html(markdown_text)
        theme = self.themes[self.current_theme]
        
        styled_html = f"""
        <html>
            <head>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                        padding: 20px 30px; 
                        line-height: 1.6;
                        max-width: 900px;
                        margin: 0 auto;
                        color: {theme['preview_fg']};
                        background-color: {theme['preview_bg']};
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        color: {theme['preview_fg']};
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid {theme['hover_bg']}; padding-bottom: .3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid {theme['hover_bg']}; padding-bottom: .3em; }}
                    code {{ 
                        background-color: {theme['hover_bg']};
                        padding: 0.2em 0.4em;
                        border-radius: 3px;
                        font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
                        font-size: 85%;
                    }}
                    pre {{ 
                        background-color: {theme['hover_bg']};
                        padding: 16px;
                        border-radius: 6px;
                        overflow: auto;
                        line-height: 1.45;
                    }}
                    pre code {{
                        background-color: transparent;
                        padding: 0;
                        border-radius: 0;
                    }}
                    blockquote {{ 
                        border-left: 4px solid {theme['hover_bg']};
                        margin: 0;
                        padding: 0 1em;
                        color: {theme['preview_fg']};
                        opacity: 0.8;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 16px 0;
                    }}
                    th, td {{
                        border: 1px solid {theme['hover_bg']};
                        padding: 6px 13px;
                    }}
                    th {{
                        background-color: {theme['hover_bg']};
                        font-weight: 600;
                    }}
                    tr:nth-child(2n) {{
                        background-color: {theme['hover_bg']};
                    }}
                    a {{
                        color: {theme['selected_bg']};
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
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
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Rename", command=self.rename_file)
        context_menu.add_command(label="Delete", command=self.delete_file)
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

    def delete_file(self):
        """处理文件删除的前端逻辑"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a file or directory.")
            return

        full_path = self.get_full_path(selected_item[0])
        item_name = self.tree.item(selected_item[0], "text")
        
        # 确认删除
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            # 调用后端删除方法
            success, error_msg = self.file_manager.delete_file(full_path)
            
            if success:
                # 从树形视图中移除节点
                self.tree.delete(selected_item[0])
                messagebox.showinfo("Success", f"'{item_name}' has been deleted successfully!")
                
                # 如果当前打开的文件被删除，清空编辑器
                if hasattr(self.file_manager, 'current_file_path') and \
                   self.file_manager.current_file_path == full_path:
                    self.text_area.delete("1.0", tk.END)
                    self.root.title("Knowgent")
                    self.file_manager.current_file_path = None
            else:
                messagebox.showerror("Error", f"Failed to delete: {error_msg}")

    def cut_text(self):
        self.copy_text()
        self.text_area.delete("sel.first", "sel.last")

    def copy_text(self):
        self.root.clipboard_clear()
        try:
            text = self.text_area.get("sel.first", "sel.last")
            self.root.clipboard_append(text)
        except tk.TclError:
            pass

    def paste_text(self):
        try:
            text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, text)
        except tk.TclError:
            pass

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