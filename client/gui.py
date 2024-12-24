import os
import re
from pathlib import Path
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinterweb import HtmlFrame
from .menu_builder import MenuBuilder
from .text_processor import TextProcessor
from .notebookselect import NotebookSelectionDialog
from .llm import llmagent
from server.application.services.notebook_service import NotebookService
from server.application.services.note_service import NoteService
from server.application.services.note_tag_service import NoteTagService
from server.application.services.tag_service import TagService
from server.application.exceptions import NoteTagError

class KnowgentGUI:
    def __init__(self, root, db):
        self.root = root
        self.text_processor = TextProcessor()
        self.markdown_mode = False
        self.chat_mode=False
        self.chat=llmagent()
        
        #当前打开的笔记/笔记本
        self.current_notebook = None
        self.current_note = None

        # 初始化后端服务
        self.notebook_service = NotebookService(db)  # 初始化 NotebookService
        self.note_service = NoteService(db)  # 初始化 NoteService
        self.note_tag_service = NoteTagService(db)  #初始化 NoteTagService
        self.tag_service = TagService(db)  #初始化 TagService
        
        # Inject services
        self.notebook_service.note_service = self.note_service
        self.note_service.notebook_service = self.notebook_service
        self.note_tag_service.note_service = self.note_service
        self.note_tag_service.tag_service = self.tag_service
        
        self.is_left_frame_visible = False
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
        self.paned_window.add(self.editor_frame,weight=3)

        # 创建编辑器顶部框架
        self.editor_top_frame = ttk.Frame(self.editor_frame, style='Custom.TFrame')
        self.editor_top_frame.pack(fill=tk.X, padx=5, pady=5)

        # 创建一个空的填充框架
        self.spacer = ttk.Frame(self.editor_top_frame, style='Custom.TFrame')
        self.spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 创建一个标签展示区
        self.tag_text = ""  # 初始化标签文本
        self.tag_label = ttk.Label(
            self.spacer,
            text="Double click here to edit tags...",
            background=self.themes[self.current_theme]['bg'],
            foreground=self.themes[self.current_theme]['fg'],
            font=('Arial', 10)
       )
        self.tag_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.tag_label.bind("<Double-1>", self.edit_tags) 
        
        # 添加Markdown预览按钮
        self.markdown_button = ttk.Button(
            self.editor_top_frame, 
            text="Preview",
            width=8,
            style='Preview.TButton',
            command=self.toggle_markdown_preview
        )
        self.markdown_button.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # 添加保存按钮
        save_button = ttk.Button(
            self.editor_top_frame, 
            text="Save",
            width=8,
            style='Preview.TButton',
            command=self.save_note
        )
        save_button.pack(side=tk.RIGHT, padx=5, pady=2)
        
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

        self.chat_button = tk.Button(editor_container, 
                                      text="Knowgent", 
                                      height=3,
                                      width=8,
                                      bg="#DEDEDE", 
                                      fg="black", 
                                      font=("Arial", 12), 
                                    command=self.toggle_chat, 
                                    relief="ridge", 
                                    borderwidth=0.5
                                    )
        self.chat_button.tkraise()
        self.chat_button.pack(side=tk.RIGHT, padx=30, pady=30)
        self.root.bind('<Control-k>', lambda e:self.toggle_chat())     

        self.chat_window= self.chat.create_chat(self.paned_window)

        self.chat.tag_button.config(command=lambda: self.chat.create_tag(self.text_area.get("1.0", tk.END)))
        self.chat.outline_button.config(command=lambda: self.chat.create_outline(self.text_area.get("1.0", tk.END)))
        # 创建预览区
        self.preview_frame = ttk.Frame(self.paned_window, style='Custom.TFrame')
        self.preview_area = HtmlFrame(self.preview_frame, messages_enabled=False)
        self.preview_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 绑定事件
        self.text_area.bind('<<Modified>>', self.on_text_modified)

        
        
                
        
        # 创建文件浏览器
        self.create_file_browser()

    def update_button_position(self,button):
        """动态计算按钮初始位置（右下角）"""
        button_width = 40
        button_height = 40
        frame_width = self.editor_frame.winfo_width()
        frame_height = self.editor_frame.winfo_height()
        x = frame_width - button_width - 10  # 距离右边和下边各留 10px 间距
        y = frame_height - button_height - 10
        button.place(x=x, y=y, width=button_width, height=button_height)
        button.tkraise()
    
    def create_file_browser(self):
        # 添加"创建 Notebook"按钮
        create_notebook_button = ttk.Button(
            self.file_browser_frame,
            text="Create Notebook",
            command=self.create_notebook,
            style='Preview.TButton',
        )
        create_notebook_button.pack(side=tk.TOP, pady=10)  # 将按钮放置在顶部

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
        self.tree.heading('#0', text="Notebooks and Notes", anchor='w')

        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # 初始化笔记本和笔记
        self.populate_tree()


    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        # 获取所有笔记本
        notebooks = self.notebook_service.get_all_notebooks()
        for notebook in notebooks:
            notebook_node = self.tree.insert("", "end", text=notebook['notebook_name'], open=True)
            # 获取笔记本中的所有笔记
            notes = self.note_service.get_all_notes_in_notebook(notebook['notebook_name'])
            for note in notes:
                self.tree.insert(notebook_node, "end", text=note['title'], open=False)


    def on_double_click(self, event):
        """
        双击打开笔记并加载内容
        """
        item = self.tree.selection()[0]
        item_type = self.tree.parent(item)  # 判断是笔记本还是笔记
        if item_type:  # 如果是笔记
            notebook_name = self.tree.item(item_type, "text")
            note_title = self.tree.item(item, "text")
            self.current_notebook = notebook_name
            self.current_note = note_title
            try:
                # 获取笔记内容
                content = self.note_service.get_note_content(note_title, notebook_name)
                self.text_area.delete(1.0, tk.END)  # 清空编辑区
                self.text_area.insert(tk.END, content)  # 显示笔记内容
                self.root.title(f"Knowgent - {note_title} in {notebook_name}")  # 更新窗口标题

                # 查询笔记的标签
                tags = self.note_tag_service.get_tags_for_note(note_title, notebook_name)
                self.tag_text = "; ".join(tags) if tags else ""  # 更新 self.tag_text
                self.render_tags(tags)  # 渲染标签

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load note: {str(e)}")
        else:  # 如果是笔记本
            notebook_name = self.tree.item(item, "text")
            self.tree.item(item, open=not self.tree.item(item, "open"))  # 展开或收起笔记本


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
            self.paned_window.add(self.preview_frame,weight=9)  # 添加预览窗口
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

    
    def show_context_menu(self, event):
        """显示右键上下文菜单"""
        selected_item = self.tree.identify_row(event.y)  # 获取右键点击的项
        if not selected_item:
            return

        context_menu = tk.Menu(self.root, tearoff=0)
        item_type = self.tree.parent(selected_item)  # 判断是笔记本还是笔记
        if item_type:  # 如果是笔记
            context_menu.add_command(label="Rename Note", command=self.rename_note)
            context_menu.add_command(label="Delete Note", command=self.delete_note)
        else:  # 如果是笔记本
            context_menu.add_command(label="Create Note", command=lambda: self.create_note(selected_item))  # 创建笔记选项
            context_menu.add_command(label="Rename Notebook", command=lambda: self.rename_notebook(selected_item))  # 重命名笔记本选项
            context_menu.add_command(label="Delete Notebook", command=lambda: self.delete_notebook(selected_item))  # 删除笔记本选项
        context_menu.post(event.x_root, event.y_root)

    def rename_selected_item(self, event=None):
        """
        重命名选中的笔记本或笔记
        """
        selected_item = self.tree.selection()
        if not selected_item:
            # messagebox.showwarning("No Selection", "Please select a notebook or note to delete.")
            return

        item_type = self.tree.parent(selected_item[0])  # 判断是笔记本还是笔记

        if item_type:  # 如果是笔记
            self.rename_note()  # 调用重命名笔记的函数
        else:  # 如果是笔记本
            self.rename_notebook(selected_item)  # 调用删除笔记本的函数

    def delete_selected_item(self, event=None):
        """
        删除选中的笔记本或笔记
        """
        selected_item = self.tree.selection()
        if not selected_item:
            # messagebox.showwarning("No Selection", "Please select a notebook or note to delete.")
            return

        item_type = self.tree.parent(selected_item[0])  # 判断是笔记本还是笔记

        if item_type:  # 如果是笔记
            self.delete_note()  # 调用删除笔记的函数
        else:  # 如果是笔记本
            self.delete_notebook(selected_item)  # 调用删除笔记本的函数

    def create_notebook(self):
        """创建新的 Notebook"""
        # 弹出对话框，输入 Notebook 名称（必填）
        notebook_name = simpledialog.askstring("Create Notebook", "Enter the name of the new notebook:", parent=self.root)
        if not notebook_name:
            # messagebox.showwarning("Warning", "Notebook name is required. Operation cancelled.")
            return

        # 弹出对话框，输入 Notebook 描述（选填）
        description = simpledialog.askstring("Create Notebook", "Enter a description for the new notebook (optional):", parent=self.root)

        # 调用后端服务创建 Notebook
        try:
            success = self.notebook_service.create_notebook(notebook_name=notebook_name, description=description)
            if success:
                messagebox.showinfo("Success", f"Notebook '{notebook_name}' created successfully!")
                self.populate_tree()  # 刷新树形结构
            else:
                messagebox.showerror("Error", f"Failed to create notebook '{notebook_name}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create notebook: {str(e)}")

    def rename_notebook(self, notebook_item):
        """重命名笔记本"""
        old_notebook_name = self.tree.item(notebook_item, "text")  # 获取当前笔记本名称
        new_notebook_name = simpledialog.askstring("Rename Notebook", "Enter new notebook name:", initialvalue=old_notebook_name, parent=self.root)  # 弹窗输入新名称
        if new_notebook_name and new_notebook_name != old_notebook_name:
            try:
                success = self.notebook_service.update_notebook(notebook_name=old_notebook_name, new_name=new_notebook_name)  # 调用后端服务重命名笔记本
                if success:
                    self.populate_tree()  # 刷新树形结构
                    messagebox.showinfo("Success", f"Notebook renamed to '{new_notebook_name}' successfully!")
                else:
                    messagebox.showerror("Error", f"Failed to rename notebook '{old_notebook_name}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename notebook: {str(e)}")

    def delete_notebook(self, notebook_item):
        """删除笔记本及其所有笔记"""
        notebook_name = self.tree.item(notebook_item, "text")  # 获取笔记本名称
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete notebook '{notebook_name}' and all its notes?"):
            try:
                # 获取该笔记本下的所有笔记
                notes = self.note_service.get_all_notes_in_notebook(notebook_name)  # 获取所有笔记
                for note in notes:
                    self.note_service.delete_note(note['title'], notebook_name)  # 删除每个笔记
                
                # 删除笔记本
                self.notebook_service.delete_notebook(notebook_name)
                self.populate_tree()  # 刷新树形结构
                messagebox.showinfo("Success", f"Notebook '{notebook_name}' and all its notes deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete notebook '{notebook_name}': {str(e)}")

    # 右键创建笔记
    def create_note(self, notebook_item):
        """创建新笔记"""
        notebook_name = self.tree.item(notebook_item, "text")  # 获取笔记本名称
        note_title = simpledialog.askstring("Create Note", "Enter note title:", parent=self.root)  # 弹窗输入笔记标题
        if note_title:
            try:
                success = self.note_service.create_note(note_title, notebook_name)  # 调用后端服务创建笔记
                if success:
                    self.populate_tree()  # 刷新树形结构
                    messagebox.showinfo("Success", f"Note '{note_title}' created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create note: {str(e)}")

    # 在菜单栏中创建笔记
    def create_note_in_menu(self):
        notebook_name = NotebookSelectionDialog.select_notebook(self.root, self.notebook_service)
        if notebook_name:
            note_title = simpledialog.askstring("Create Note", "Enter note title:", parent=self.root)
            if note_title:
                try:
                    success = self.note_service.create_note(note_title, notebook_name)
                    if success:
                        self.populate_tree()
                        messagebox.showinfo("Success", f"Note '{note_title}' created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create note: {str(e)}")

    def delete_note(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a note.")
            return

        notebook_name = self.tree.item(self.tree.parent(selected_item[0]), "text")
        note_title = self.tree.item(selected_item[0], "text")
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{note_title}'?"):
            try:
                success = self.note_service.delete_note(note_title, notebook_name)
                if success:
                    self.populate_tree()  # 刷新树形结构
                    messagebox.showinfo("Success", f"Note '{note_title}' deleted successfully!")
                    # 被删除的笔记是正在编辑区的笔记
                    if self.current_note == note_title and self.current_notebook == notebook_name:
                        self.text_area.delete(1.0, tk.END)  # 清空编辑区
                        self.current_notebook = None  # 重置当前笔记本
                        self.current_note = None  # 重置当前笔记
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {str(e)}")

    def rename_note(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a note.")
            return

        notebook_name = self.tree.item(self.tree.parent(selected_item[0]), "text")
        old_title = self.tree.item(selected_item[0], "text")
        new_title = simpledialog.askstring("Rename Note", "Enter new note title:", initialvalue=old_title, parent=self.root)
        if new_title and new_title != old_title:
            try:
                success = self.note_service.update_note(old_title, notebook_name, new_title=new_title)
                if success:
                    self.populate_tree()  # 刷新树形结构
                    messagebox.showinfo("Success", f"Note renamed to '{new_title}' successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename note: {str(e)}")

    def save_file(self, content, file_path=None):
        if not file_path:
            return False
            
        try: 
            with open(file_path, "w") as file:
                file.write(content)
        except:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
                return False
        return True

        # try:
        #     with open(file_path, 'w') as file:
        #         file.write(content)
        #     # messagebox.showinfo("Success", f"File saved successfully at {save_path}")
        #     return True
        # except Exception as e:
        #     messagebox.showerror("Error", f"Could not save file: {e}")
        #     return False

    def save_note(self):
        """
        保存当前编辑区的内容到笔记
        """
        if not self.current_note:
            # 如果没有打开的笔记，调用 save_note_as 函数
            self.save_note_as()
            return

        notebook_name = self.current_notebook
        note_title = self.current_note
        content = self.text_area.get(1.0, tk.END)  # 获取编辑区的内容

        try:
            # 获取笔记的文件路径
            file_path = self.note_service.get_note_file_path(note_title, notebook_name)

            # 保存内容到文件
            if self.save_file(content, file_path):
                messagebox.showinfo("Success", f"Note '{note_title}' saved successfully!")
            else:
                messagebox.showerror("Error", f"Failed to save note '{note_title}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note: {str(e)}")

    def save_note_as(self):
        """
        保存当前编辑区的内容为一个新的笔记
        """
        # 弹出笔记本选择对话框，获取用户选择的笔记本名称
        notebook_name = NotebookSelectionDialog.select_notebook(self.root, self.notebook_service)
        if not notebook_name:
            messagebox.showinfo("Info", "No notebook selected. Operation cancelled.")
            return

        # 弹出对话框，输入新的笔记标题
        note_title = simpledialog.askstring("Save Note As", "Enter the title for the new note:", parent=self.root)
        if not note_title:
            messagebox.showinfo("Info", "Note title is required. Operation cancelled.")
            return

        # 获取当前编辑区的内容
        content = self.text_area.get(1.0, tk.END)

        try:
            # 在选定的笔记本中创建新的笔记
            success = self.note_service.create_note(note_title, notebook_name)
            if success:
                # 获取新笔记的文件路径
                file_path = self.note_service.get_note_file_path(note_title, notebook_name)

                # 保存内容到文件
                if self.save_file(content, file_path):
                    messagebox.showinfo("Success", f"Note '{note_title}' saved successfully in notebook '{notebook_name}'!")
                    self.current_notebook = notebook_name
                    self.current_note = note_title
                    self.tag_text = ""
                    self.populate_tree()  # 刷新树形结构
                else:
                    messagebox.showerror("Error", f"Failed to save note '{note_title}'.")
            else:
                messagebox.showerror("Error", f"Failed to create note '{note_title}' in notebook '{notebook_name}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note: {str(e)}")

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

    def edit_tags(self, event):
        # 未选中笔记时无法编辑tag
        if not self.current_note:
            return

        # 编辑标签文本
        new_tags = simpledialog.askstring("Edit Tags", "Edit tags of the note (separated by ';' or '；'): ", initialvalue=self.tag_text, parent=self.root)
        if new_tags is not None:  # 用户点击确定
            # 格式化标签并生成tag_list
            tag_list = [tag.strip() for tag in re.split(r'[;；]', new_tags) if tag.strip()]  # 去除空格并过滤空标签

            # 调用后端服务获取该笔记的现有标签
            try:
                existing_tags = self.note_tag_service.get_tags_for_note(self.current_note, self.current_notebook)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch existing tags: {str(e)}")
                return

            # 将现有标签和新的标签列表转换为集合，方便对比
            existing_tags_set = set(existing_tags)
            new_tags_set = set(tag_list)

            # 计算需要添加的标签和需要删除的标签
            tags_to_add = new_tags_set - existing_tags_set
            tags_to_remove = existing_tags_set - new_tags_set

            # 添加新标签
            for tag in tags_to_add:
                try:
                    self.note_tag_service.add_tag_to_note(self.current_note, self.current_notebook, tag)
                except NoteTagError:
                    try:
                        self.tag_service.create_tag(tag)  # 调用 tag_service 创建 tag
                        self.note_tag_service.add_tag_to_note(self.current_note, self.current_notebook, tag)  # 重新添加标签
                    except Exception as e:
                        pass
                        messagebox.showerror("Error", f"Failed to create tag '{tag}': {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add tag '{tag}': {str(e)}")

            # 删除不再需要的标签
            for tag in tags_to_remove:
                try:
                    self.note_tag_service.remove_tag_from_note(self.current_note, self.current_notebook, tag)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove tag '{tag}': {str(e)}")

            # 更新 self.tag_text
            self.tag_text = '; '.join(tag_list) + '; '  # 保存用户输入的标签

            # 清空当前标签显示
            for widget in self.spacer.winfo_children():
                if widget.winfo_exists():  # 检查组件是否存在
                    widget.destroy()

            # 渲染标签
            self.render_tags(tag_list)

    def render_tags(self, tag_list):
        # 清空当前标签显示
        for widget in self.spacer.winfo_children():
            if widget.winfo_exists():  # 检查组件是否存在
                widget.destroy()

        """根据 tag_list 渲染标签"""
        if not tag_list:
            # 如果标签列表为空，显示提示文本
            self.tag_label = tk.Label(
                self.spacer,
                text="Double click here to edit tags...",
                background=self.themes[self.current_theme]['bg'],
                foreground=self.themes[self.current_theme]['fg'],
                font=('Arial', 10)
            )
            self.tag_label.pack(side=tk.LEFT, padx=5, pady=5)
            self.tag_label.bind("<Double-1>", self.edit_tags)  # 重新绑定事件
        else:
            # 生成小方块显示标签
            for tag in tag_list:
                tag_color = self.get_color_from_string(tag)  # 根据标签内容生成颜色
                tag_frame = tk.Frame(self.spacer, bg=tag_color, width=60, height=20)  # 调整小方块的尺寸
                tag_frame.pack(side=tk.LEFT, padx=2, pady=2)
                tag_label = tk.Label(tag_frame, text=tag, bg=tag_color, fg='white')  # 将标签放入小方块中
                tag_label.pack(fill=tk.BOTH, expand=True)  # 使标签填充小方块
                tag_label.bind("<Double-1>", self.edit_tags)  # 绑定事件到每个标签

            # 添加一个占位符，用于点击编辑标签
            placeholder_label = tk.Label(
                self.spacer,
                text="",
                background=self.themes[self.current_theme]['bg'],
                foreground=self.themes[self.current_theme]['fg'],
                font=('Arial', 10)
            )
            placeholder_label.pack(side=tk.LEFT, padx=5, pady=5)
            placeholder_label.bind("<Double-1>", self.edit_tags)  # 绑定事件到占位符
    
    def get_color_from_string(self, tag):
        """根据字符串生成固定颜色"""
        # 使用 SHA-256 哈希算法计算字符串的哈希值
        hash_object = hashlib.sha256(tag.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # 取哈希值的前6个字符作为颜色值
        color_hex = hash_hex[:6]
        return f'#{color_hex}'

    # ================= 悬浮按钮功能 ================= #
    def toggle_chat(self):
        self.chat_mode = not self.chat_mode
        if self.chat_mode:
            self.paned_window.add(self.chat_window,weight=5) # 显示左侧窗口
        else:
            self.paned_window.remove(self.chat_window) # 隐藏左侧窗口
