import tkinter as tk

class MenuBuilder:
    def __init__(self, gui):
        self.gui = gui
        self.root = gui.root
        self.theme_var = tk.BooleanVar(value=False)
        self.create_menu()
        self.bind_shortcuts()

    def create_menu(self):
        # 创建主菜单栏并设置样式
        menu_bar = tk.Menu(
            self.root,
            relief=tk.FLAT,
            border=0,
            activeborderwidth=0,  # 移除激活时的边框
            bd=0  # 移除边框
        )
        
        # 创建子菜单
        file_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            relief=tk.FLAT,
            border=0,
            activeborderwidth=0,
            bd=0
        )
        edit_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            relief=tk.FLAT,
            border=0,
            activeborderwidth=0,
            bd=0
        )
        view_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            relief=tk.FLAT,
            border=0,
            activeborderwidth=0,
            bd=0
        )

        # 文件菜单
        file_menu.add_command(label="Open", command=self.gui.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.gui.save_note, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.gui.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Select Directory", command=self.gui.select_directory)  # 添加选择目录
        file_menu.add_command(label="New File", command=self.gui.create_new_file)  # 添加新建文件
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        edit_menu.add_command(label="Cut", command=self.gui.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.gui.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.gui.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.gui.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.gui.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.gui.replace_text, accelerator="Ctrl+H")

        view_menu.add_checkbutton(
            label="Dark Theme",
            variable=self.theme_var,
            command=self.toggle_theme
        )

        # 添加级联菜单
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)

        # 配置根窗口的菜单
        self.root.config(menu=menu_bar)
        
        # 保存菜单引用
        self.menu_bar = menu_bar
        self.file_menu = file_menu
        self.edit_menu = edit_menu
        self.view_menu = view_menu

    def update_menu_colors(self, bg_color, fg_color):
        """更新菜单栏颜色"""
        def configure_menu(menu):
            menu.configure(
                bg=bg_color,
                fg=fg_color,
                activebackground=fg_color,
                activeforeground=bg_color,
                selectcolor=fg_color,
                disabledforeground=fg_color
            )
            
        # 配置所有菜单
        for menu in [self.menu_bar, self.file_menu, self.edit_menu, self.view_menu]:
            configure_menu(menu)
            
        # 特别处理顶层菜单栏
        self.menu_bar.configure(
            bg=bg_color,
            fg=fg_color,
            activebackground=bg_color,
            activeforeground=fg_color,
            activeborderwidth=0,
            bd=0
        )
        
        # 强制更新菜单显示
        self.root.update_idletasks()
        
        # 尝试更新顶层菜单的外观
        try:
            self.root.tk.call('tk_menuBar', self.menu_bar, bg_color)
            self.root.tk.call('tk_setPalette', 'background', bg_color)
        except:
            pass

    def toggle_theme(self):
        """切换主题"""
        if self.theme_var.get():
            self.gui.change_theme('Dark')
        else:
            self.gui.change_theme('Light')

    def bind_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self.gui.open_file())
        self.root.bind('<Control-s>', lambda e: self.gui.save_note())
        self.root.bind('<Control-S>', lambda e: self.gui.save_file_as())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-f>', lambda e: self.gui.find_text())
        self.root.bind('<Control-h>', lambda e: self.gui.replace_text())
        self.root.bind('<Control-a>', lambda e: self.gui.select_all())